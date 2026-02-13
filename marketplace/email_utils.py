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
