"""
Payment utilities for Stripe and Razorpay integration
"""
import stripe
import razorpay
from django.conf import settings
from decimal import Decimal

# Initialize Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

# Initialize Razorpay
razorpay_client = razorpay.Client(auth=(
    getattr(settings, 'RAZORPAY_KEY_ID', ''),
    getattr(settings, 'RAZORPAY_KEY_SECRET', '')
))


def create_stripe_checkout_session(order, success_url, cancel_url):
    """
    Create a Stripe Checkout session for an order
    
    Args:
        order: Order instance
        success_url: URL to redirect on success
        cancel_url: URL to redirect on cancel
        
    Returns:
        Stripe checkout session
    """
    try:
        # Convert price to cents (Stripe uses smallest currency unit)
        amount_in_cents = int(order.total_price * 100)
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',  # Indian Rupees
                    'unit_amount': amount_in_cents,
                    'product_data': {
                        'name': order.book.title,
                        'description': f'by {order.book.author}',
                        'images': [order.book.get_primary_image().url] if order.book.get_primary_image() else [],
                    },
                },
                'quantity': order.quantity,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=str(order.id),
            metadata={
                'order_id': order.id,
                'buyer_id': order.buyer.id,
                'seller_id': order.seller.id,
            }
        )
        
        return session
        
    except Exception as e:
        print(f"Error creating Stripe session: {e}")
        return None


def create_razorpay_order(order):
    """
    Create a Razorpay order
    
    Args:
        order: Order instance
        
    Returns:
        Razorpay order dict
    """
    try:
        # Convert price to paise (Razorpay uses smallest currency unit)
        amount_in_paise = int(order.total_price * 100)
        
        razorpay_order = razorpay_client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": f"order_{order.id}",
            "notes": {
                "order_id": str(order.id),
                "buyer_id": str(order.buyer.id),
                "seller_id": str(order.seller.id),
                "book_title": order.book.title,
            }
        })
        
        return razorpay_order
        
    except Exception as e:
        print(f"Error creating Razorpay order: {e}")
        return None


def verify_razorpay_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    """
    Verify Razorpay payment signature
    
    Args:
        razorpay_order_id: Razorpay order ID
        razorpay_payment_id: Razorpay payment ID
        razorpay_signature: Razorpay signature
        
    Returns:
        True if valid, False otherwise
    """
    try:
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })
        return True
    except:
        return False


def process_razorpay_payment(razorpay_payment_id, razorpay_order_id):
    """
    Process a successful Razorpay payment
    
    Args:
        razorpay_payment_id: Razorpay payment ID
        razorpay_order_id: Razorpay order ID
        
    Returns:
        Order instance if successful, None otherwise
    """
    from .models import Order, Payment
    from .email_utils import send_order_confirmation_email, send_new_order_notification_email
    
    try:
        # Get payment details from Razorpay
        payment_details = razorpay_client.payment.fetch(razorpay_payment_id)
        order_details = razorpay_client.order.fetch(razorpay_order_id)
        
        order_id = order_details['notes'].get('order_id')
        order = Order.objects.get(id=order_id)
        
        # Update order status
        order.mark_as_paid(razorpay_payment_id)
        order.payment_gateway = 'razorpay'
        order.save()
        
        # Create payment record
        Payment.objects.create(
            order=order,
            payment_id=razorpay_payment_id,
            payment_method=payment_details.get('method', 'unknown'),
            amount=Decimal(payment_details['amount']) / 100,  # Convert from paise
            status='completed',
            payment_gateway='razorpay',
            metadata={
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'email': payment_details.get('email'),
                'contact': payment_details.get('contact'),
            }
        )
        
        # Mark book as sold
        order.book.status = 'sold'
        order.book.save()
        
        # Send email notifications
        send_order_confirmation_email(order)
        send_new_order_notification_email(order)
        
        return order
        
    except Order.DoesNotExist:
        print(f"Order not found for razorpay order {razorpay_order_id}")
        return None
    except Exception as e:
        print(f"Error processing Razorpay payment: {e}")
        return None


def verify_stripe_webhook_signature(payload, sig_header):
    """
    Verify Stripe webhook signature
    
    Args:
        payload: Request body
        sig_header: Stripe signature header
        
    Returns:
        Event object if valid, None otherwise
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        return event
    except ValueError:
        # Invalid payload
        return None
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return None


def process_successful_payment(session):
    """
    Process a successful Stripe payment
    
    Args:
        session: Stripe checkout session
        
    Returns:
        Order instance if successful, None otherwise
    """
    from .models import Order, Payment
    from .email_utils import send_order_confirmation_email, send_new_order_notification_email
    
    try:
        order_id = session.metadata.get('order_id')
        order = Order.objects.get(id=order_id)
        
        # Update order status
        order.mark_as_paid(session.payment_intent)
        order.payment_gateway = 'stripe'
        order.save()
        
        # Create payment record
        Payment.objects.create(
            order=order,
            payment_id=session.payment_intent,
            payment_method='card',
            amount=Decimal(session.amount_total) / 100,  # Convert from cents
            status='completed',
            payment_gateway='stripe',
            metadata={
                'session_id': session.id,
                'customer_email': session.customer_details.get('email'),
            }
        )
        
        # Mark book as sold
        order.book.status = 'sold'
        order.book.save()
        
        # Send email notifications
        send_order_confirmation_email(order)
        send_new_order_notification_email(order)
        
        return order
        
    except Order.DoesNotExist:
        print(f"Order not found for session {session.id}")
        return None
    except Exception as e:
        print(f"Error processing payment: {e}")
        return None


def create_refund(payment_id, amount=None):
    """
    Create a Stripe refund
    
    Args:
        payment_id: Stripe payment intent ID
        amount: Amount to refund in cents (None for full refund)
        
    Returns:
        Refund object if successful, None otherwise
    """
    try:
        refund = stripe.Refund.create(
            payment_intent=payment_id,
            amount=amount,
        )
        return refund
    except Exception as e:
        print(f"Error creating refund: {e}")
        return None
