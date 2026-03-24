"""
Email notification utilities
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def send_welcome_email(user):
    """Send welcome email to new user"""
    subject = 'Welcome to BOOKCYCLE! 📚'
    
    html_message = render_to_string('marketplace/emails/welcome.html', {
        'user': user,
    })
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False


def send_activation_email(user, domain):
    """Send activation email to new user"""
    from .tokens import account_activation_token
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes
    
    subject = 'Activate your BOOKCYCLE account'
    
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    
    html_message = render_to_string('marketplace/emails/activation_email.html', {
        'user': user,
        'domain': domain,
        'uid': uid,
        'token': token,
    })
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending activation email: {e}")
        return False


def send_order_confirmation_email(order):
    """Send order confirmation email to buyer"""
    subject = f'Order Confirmation #{order.id} - BOOKCYCLE'
    
    html_message = render_to_string('marketplace/emails/order_confirmation.html', {
        'order': order,
        'buyer': order.buyer,
    })
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [order.buyer.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending order confirmation email: {e}")
        return False


def send_new_order_notification_email(order):
    """Send new order notification email to seller"""
    subject = f'New Order Received #{order.id} - BOOKCYCLE'
    
    html_message = render_to_string('marketplace/emails/new_order_seller.html', {
        'order': order,
        'seller': order.seller,
    })
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [order.seller.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending new order notification email: {e}")
        return False


def send_order_shipped_email(order):
    """Send order shipped email to buyer"""
    subject = f'Your Order #{order.id} Has Been Shipped! 📦'
    
    html_message = render_to_string('marketplace/emails/order_shipped.html', {
        'order': order,
        'buyer': order.buyer,
    })
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [order.buyer.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending order shipped email: {e}")
        return False


def send_tracking_update_email(order):
    """Send tracking update email to buyer"""
    subject = f'Tracking Information Added - Order #{order.id} 📦'
    
    # Get courier service display name
    courier_display = dict(order._meta.get_field('courier_service').choices).get(
        order.courier_service, order.courier_service)
    
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2563eb;">📦 Order Status Update</h2>
            <p>Hi {order.buyer.get_full_name()},</p>
            <p>Your order status has been updated by the seller. Here are the latest details:</p>
            
            <div style="background: #f9fafb; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0;">Order #{order.id}</h3>
                <p><strong>Book:</strong> {order.book.title}</p>
                <p><strong>Total:</strong> ₹{order.total_price}</p>
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 15px 0;">
                <p><strong>📑 Current Status:</strong> <span style="color: #2563eb; font-weight: bold;">{order.get_shipping_status_display()}</span></p>
                <p><strong>📦 Courier Service:</strong> {courier_display}</p>
                <p><strong>🔢 Tracking Number:</strong> <code style="background: #fff; padding: 5px 10px; border-radius: 4px; font-size: 1.1em;">{order.tracking_number}</code></p>
                {f'<p><strong>📅 Expected Delivery:</strong> {order.estimated_delivery_date.strftime("%B %d, %Y")}</p>' if order.estimated_delivery_date else ''}
            </div>
            
            <p>You can use the tracking number above to track your shipment on the courier's website.</p>
            <p>Thank you for shopping with BOOKCYCLE! 📚</p>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 0.875rem;">
                <p>BOOKCYCLE - Your marketplace for buying and selling books</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [order.buyer.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending tracking update email: {e}")
        return False


def send_order_completed_email(order):
    """Send order completed email to buyer"""
    subject = f'Order #{order.id} Completed - Leave a Review! ⭐'
    
    html_message = render_to_string('marketplace/emails/order_completed.html', {
        'order': order,
        'buyer': order.buyer,
    })
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [order.buyer.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending order completed email: {e}")
        return False


def send_order_cancelled_email(order):
    """Send order cancelled email to both buyer and seller"""
    subject = f'Order #{order.id} Cancelled'
    
    # Email to buyer
    html_message_buyer = render_to_string('marketplace/emails/order_cancelled_buyer.html', {
        'order': order,
    })
    plain_message_buyer = strip_tags(html_message_buyer)
    
    # Email to seller
    html_message_seller = render_to_string('marketplace/emails/order_cancelled_seller.html', {
        'order': order,
    })
    plain_message_seller = strip_tags(html_message_seller)
    
    try:
        # Send to buyer
        send_mail(
            subject,
            plain_message_buyer,
            settings.DEFAULT_FROM_EMAIL,
            [order.buyer.email],
            html_message=html_message_buyer,
            fail_silently=False,
        )
        
        # Send to seller
        send_mail(
            subject,
            plain_message_seller,
            settings.DEFAULT_FROM_EMAIL,
            [order.seller.email],
            html_message=html_message_seller,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending order cancelled emails: {e}")
        return False
