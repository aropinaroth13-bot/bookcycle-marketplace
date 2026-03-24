from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from .models import Book, UserProfile, CartItem, Order, Payment, BookReview, Wishlist, Conversation, Message
from .forms import UserRegistrationForm, UserProfileForm, BookListingForm, BookSearchForm, CheckoutForm, BookReviewForm, MessageForm
from django.contrib.auth.models import User
from .payment_utils import create_stripe_checkout_session, verify_stripe_webhook_signature, process_successful_payment
import json


# Home Page
def home(request):
    """Homepage with latest book listings"""
    books = Book.objects.filter(status='available').order_by('-created_at')[:12]
    context = {
        'books': books,
        'categories': Book.CATEGORY_CHOICES,
    }
    return render(request, 'marketplace/home.html', context)


# Authentication Views
def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False # user must confirm email
            user.save()
            
            # Send activation email
            from .email_utils import send_activation_email
            domain = request.get_host()
            send_activation_email(user, domain)

            
            messages.success(request, f'Welcome {user.username}! Please check your email and click the link to activate your account. You will not be able to login without activation.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'marketplace/register.html', {'form': form})

def activate(request, uidb64, token):
    """Activate user account from email confirmation link"""
    from django.utils.http import urlsafe_base64_decode
    from django.utils.encoding import force_str
    from django.contrib.auth import get_user_model
    from .tokens import account_activation_token
    
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        
        # Send welcome email
        from .email_utils import send_welcome_email
        send_welcome_email(user)
        
        messages.success(request, 'Thank you for your email confirmation. Now you can login to your account.')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid or expired.')
        return redirect('home')


def user_login(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'marketplace/login.html')


@login_required
def user_logout(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile(request):
    """View user profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'marketplace/profile.html', {'profile': profile})


@login_required
def edit_profile(request):
    """Edit user profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'marketplace/edit_profile.html', {'form': form})


# Book Listing Views
def browse_books(request):
    """Browse and search books"""
    books = Book.objects.filter(status='available')
    form = BookSearchForm(request.GET)
    
    # Apply filters
    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        condition = form.cleaned_data.get('condition')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        sort_by = form.cleaned_data.get('sort_by')
        
        if query:
            books = books.filter(
                Q(title__icontains=query) |
                Q(author__icontains=query) |
                Q(description__icontains=query)
            )
        
        if category:
            books = books.filter(category=category)
        
        if condition:
            books = books.filter(condition=condition)
        
        if min_price:
            books = books.filter(price__gte=min_price)
        
        if max_price:
            books = books.filter(price__lte=max_price)
        
        # Sorting
        if sort_by == 'price_low':
            books = books.order_by('price')
        elif sort_by == 'price_high':
            books = books.order_by('-price')
        else:  # newest
            books = books.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
    }
    return render(request, 'marketplace/browse_books.html', context)


def book_detail(request, pk):
    """View book details"""
    book = get_object_or_404(Book, pk=pk)
    
    # Import utils
    from .utils import add_to_recently_viewed, get_book_stats, get_seller_stats
    
    # Add to recently viewed
    add_to_recently_viewed(request, book.id)
    
    # Get related books
    related_books = Book.objects.filter(
        category=book.category, status='available'
    ).exclude(pk=pk)[:4]
    
    # Get book stats
    book_stats = get_book_stats(book)
    
    # Get seller stats
    seller_stats = get_seller_stats(book.seller)
    
    # Check if in wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, book=book).exists()
    
    # Get recent reviews
    recent_reviews = book.reviews.all()[:3]
    
    # Get all book images
    book_images = []
    for i in range(1, 6):
        img = getattr(book, f'image{i}')
        if img:
            book_images.append(img)
    
    context = {
        'book': book,
        'related_books': related_books,
        'book_stats': book_stats,
        'seller_stats': seller_stats,
        'in_wishlist': in_wishlist,
        'recent_reviews': recent_reviews,
        'book_images': book_images,
    }
    return render(request, 'marketplace/book_detail.html', context)


@login_required
def create_listing(request):
    """Create a new book listing"""
    if request.method == 'POST':
        form = BookListingForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.seller = request.user
            book.save()
            messages.success(request, 'Book listing created successfully!')
            return redirect('my_listings')
    else:
        form = BookListingForm()
    
    return render(request, 'marketplace/create_listing.html', {'form': form})


@login_required
def edit_listing(request, pk):
    """Edit a book listing"""
    book = get_object_or_404(Book, pk=pk, seller=request.user)
    
    if request.method == 'POST':
        form = BookListingForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book listing updated successfully!')
            return redirect('my_listings')
    else:
        form = BookListingForm(instance=book)
    
    return render(request, 'marketplace/edit_listing.html', {'form': form, 'book': book})


@login_required
def delete_listing(request, pk):
    """Delete a book listing"""
    book = get_object_or_404(Book, pk=pk, seller=request.user)
    
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book listing deleted successfully!')
        return redirect('my_listings')
    
    return render(request, 'marketplace/delete_listing.html', {'book': book})


@login_required
def my_listings(request):
    """View user's book listings"""
    books = Book.objects.filter(seller=request.user).order_by('-created_at')
    return render(request, 'marketplace/my_listings.html', {'books': books})


# Shopping Cart Views
@login_required
def view_cart(request):
    """View shopping cart"""
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.get_total_price() for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'marketplace/cart.html', context)


@login_required
def add_to_cart(request, pk):
    """Add book to cart"""
    book = get_object_or_404(Book, pk=pk)
    
    if book.seller == request.user:
        messages.error(request, 'You cannot buy your own book!')
        return redirect('book_detail', pk=pk)
    
    if not book.is_available():
        messages.error(request, 'This book is not available.')
        return redirect('book_detail', pk=pk)
    
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        book=book,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f'Updated quantity of {book.title} in cart.')
    else:
        messages.success(request, f'{book.title} added to cart!')
    
    return redirect('view_cart')


@login_required
def remove_from_cart(request, pk):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, pk=pk, user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('view_cart')


@login_required
def update_cart(request, pk):
    """Update cart item quantity"""
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, pk=pk, user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated.')
        else:
            cart_item.delete()
            messages.success(request, 'Item removed from cart.')
    
    return redirect('view_cart')


# Checkout and Order Views
@login_required
def checkout(request):
    """Checkout process with payment integration"""
    cart_items = CartItem.objects.filter(user=request.user)
    
    if not cart_items:
        messages.error(request, 'Your cart is empty.')
        return redirect('view_cart')
    
    total = sum(item.get_total_price() for item in cart_items)
    profile = UserProfile.objects.get_or_create(user=request.user)[0]
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            shipping_address = form.cleaned_data['shipping_address']
            
            # Create orders for each cart item
            orders = []
            for cart_item in cart_items:
                order = Order.objects.create(
                    buyer=request.user,
                    seller=cart_item.book.seller,
                    book=cart_item.book,
                    quantity=cart_item.quantity,
                    total_price=cart_item.get_total_price(),
                    shipping_address=shipping_address,
                )
                orders.append(order)
                
                # Mark book as pending
                cart_item.book.status = 'pending'
                cart_item.book.save()
            
            # Clear cart
            cart_items.delete()
            
            # Redirect to payment page (will handle multiple orders)
            request.session['pending_order_ids'] = [o.id for o in orders]
            return redirect('process_payment')
    else:
        initial_data = {
            'shipping_address': profile.address,
            'phone_number': profile.phone_number,
        }
        form = CheckoutForm(initial=initial_data)
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'form': form,
    }
    return render(request, 'marketplace/checkout.html', context)


@login_required
def my_orders(request):
    """View buyer's orders"""
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    return render(request, 'marketplace/my_orders.html', {'orders': orders})


@login_required
def my_sales(request):
    """View seller's sales"""
    sales = Order.objects.filter(seller=request.user).order_by('-created_at')
    return render(request, 'marketplace/my_sales.html', {'sales': sales})


@login_required
def order_detail(request, pk):
    """View order details"""
    order = get_object_or_404(Order, pk=pk)
    
    # Check if user is buyer or seller
    if order.buyer != request.user and order.seller != request.user:
        messages.error(request, 'You do not have permission to view this order.')
        return redirect('home')
    
    return render(request, 'marketplace/order_detail.html', {'order': order})


@login_required
def cancel_order(request, pk):
    """Cancel an order"""
    order = get_object_or_404(Order, pk=pk, buyer=request.user)
    
    if request.method == 'POST':
        if order.status in ['pending_payment', 'paid']:
            order.cancel_order()
            messages.success(request, 'Order cancelled successfully.')
        else:
            messages.error(request, 'This order cannot be cancelled.')
        return redirect('my_orders')
    
    return render(request, 'marketplace/cancel_order_confirm.html', {'order': order})


@login_required
def update_order_tracking(request, pk):
    """Update tracking information for an order (seller only)"""
    order = get_object_or_404(Order, pk=pk, seller=request.user)
    
    if request.method == 'POST':
        from .tracking_forms import TrackingUpdateForm
        
        form = TrackingUpdateForm(request.POST)
        if form.is_valid():
            tracking_number = form.cleaned_data['tracking_number']
            courier_service = form.cleaned_data['courier_service']
            shipping_status = form.cleaned_data['shipping_status']
            estimated_delivery_date = form.cleaned_data.get('estimated_delivery_date')
            
            # Update tracking
            order.update_tracking(tracking_number, courier_service, shipping_status, estimated_delivery_date)
            
            # Send email to buyer
            try:
                from .email_utils import send_tracking_update_email
                send_tracking_update_email(order)
            except Exception as e:
                print(f"Error sending tracking email: {e}")
            
            messages.success(request, f'Order status updated to "{order.get_shipping_status_display()}"!')
            return redirect('order_detail', pk=order.id)
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        from .tracking_forms import TrackingUpdateForm
        form = TrackingUpdateForm(initial={
            'tracking_number': order.tracking_number,
            'courier_service': order.courier_service,
            'shipping_status': order.shipping_status,
            'estimated_delivery_date': order.estimated_delivery_date,
        })
    
    context = {
        'order': order,
        'form': form
    }
    return render(request, 'marketplace/update_tracking.html', context)


# Payment Views
@login_required
def process_payment(request):
    """Create Razorpay order for payment"""
    order_ids = request.session.get('pending_order_ids', [])
    
    if not order_ids:
        messages.error(request, 'No orders to process.')
        return redirect('my_orders')
    
    orders = Order.objects.filter(id__in=order_ids, buyer=request.user)
    
    if not orders:
        messages.error(request, 'Orders not found.')
        return redirect('my_orders')
    
    # For simplicity, process first order
    order = orders.first()
    
    # Import here to avoid circular imports
    from .payment_utils import create_razorpay_order
    from django.conf import settings
    
    # Create Razorpay order
    razorpay_order = create_razorpay_order(order)
    
    if razorpay_order:
        context = {
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'razorpay_order_id': razorpay_order['id'],
            'amount': order.total_price,
            'amount_in_paise': int(order.total_price * 100),
            'description': f'{order.book.title} by {order.book.author}',
        }
        return render(request, 'marketplace/process_payment.html', context)
    else:
        messages.error(request, 'Payment processing failed. Please try again.')
        return redirect('my_orders')


@login_required
def payment_success(request):
    """Payment success page"""
    session_id = request.GET.get('session_id')
    
    context = {
        'session_id': session_id,
    }
    return render(request, 'marketplace/payment_success.html', context)


@login_required
@csrf_exempt
def razorpay_callback(request):
    """Handle Razorpay payment callback"""
    if request.method == 'POST':
        from .payment_utils import verify_razorpay_payment, process_razorpay_payment
        
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')
        
        # Verify payment signature
        is_valid = verify_razorpay_payment(
            razorpay_order_id,
            razorpay_payment_id,
            razorpay_signature
        )
        
        if is_valid:
            # Process the payment
            order = process_razorpay_payment(razorpay_payment_id, razorpay_order_id)
            
            if order:
                # Clear pending orders from session
                if 'pending_order_ids' in request.session:
                    del request.session['pending_order_ids']
                
                messages.success(request, f'Payment successful! Order #{order.id} confirmed.')
                return redirect(reverse('payment_success') + f'?session_id={razorpay_payment_id}')
            else:
                messages.error(request, 'Error processing payment. Please contact support.')
                return redirect('my_orders')
        else:
            messages.error(request, 'Payment verification failed. Please contact support.')
            return redirect('payment_cancelled')
    
    return redirect('home')


@login_required
def payment_cancelled(request):
    """Payment cancelled page"""
    messages.warning(request, 'Payment was cancelled. Your orders are still pending.')
    return render(request, 'marketplace/payment_cancelled.html')


@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    event = verify_stripe_webhook_signature(payload, sig_header)
    
    if not event:
        return HttpResponse(status=400)
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Process successful payment
        order = process_successful_payment(session)
        
        if order:
            # TODO: Send email notification
            print(f"Payment successful for order {order.id}")
    
    return HttpResponse(status=200)


# Review Views
@login_required
def submit_review(request, pk):
    """Submit a review for a book"""
    book = get_object_or_404(Book, pk=pk)
    
    # Check if user already reviewed this book
    existing_review = BookReview.objects.filter(book=book, user=request.user).first()
    
    if request.method == 'POST':
        form = BookReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            
            # Check if user bought this book
            has_purchased = Order.objects.filter(
                buyer=request.user,
                book=book,
                status__in=['completed', 'shipped']
            ).exists()
            review.verified_purchase = has_purchased
            
            review.save()
            messages.success(request, 'Review submitted successfully!')
            return redirect('book_detail', pk=pk)
    else:
        form = BookReviewForm(instance=existing_review)
    
    context = {
        'book': book,
        'form': form,
        'existing_review': existing_review,
    }
    return render(request, 'marketplace/submit_review.html', context)


def book_reviews(request, pk):
    """View all reviews for a book"""
    book = get_object_or_404(Book, pk=pk)
    reviews = book.reviews.all()
    
    # Calculate average rating
    total_reviews = reviews.count()
    if total_reviews > 0:
        total_rating = sum(r.rating for r in reviews)
        average_rating = total_rating / total_reviews
    else:
        average_rating = 0
    
    context = {
        'book': book,
        'reviews': reviews,
        'total_reviews': total_reviews,
        'average_rating': average_rating,
    }
    return render(request, 'marketplace/book_reviews.html', context)


# Wishlist Views
@login_required
def wishlist(request):
    """View user's wishlist"""
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'marketplace/wishlist.html', {'wishlist_items': wishlist_items})


@login_required
def add_to_wishlist(request, pk):
    """Add book to wishlist"""
    book = get_object_or_404(Book, pk=pk)
    
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        book=book
    )
    
    if created:
        messages.success(request, f'{book.title} added to your wishlist!')
    else:
        messages.info(request, f'{book.title} is already in your wishlist.')
    
    return redirect('book_detail', pk=pk)


@login_required
def remove_from_wishlist(request, pk):
    """Remove book from wishlist"""
    wishlist_item = get_object_or_404(Wishlist, pk=pk, user=request.user)
    book_title = wishlist_item.book.title
    wishlist_item.delete()
    messages.success(request, f'{book_title} removed from wishlist.')
    return redirect('wishlist')


# Messaging Views
@login_required
def inbox(request):
    """View inbox conversations"""
    # Get all conversations where user is buyer or seller
    buyer_conversations = Conversation.objects.filter(buyer=request.user)
    seller_conversations = Conversation.objects.filter(seller=request.user)
    
    # Combine and remove duplicates
    conversations = (buyer_conversations | seller_conversations).distinct().order_by('-updated_at')
    
    # Add unread count to each conversation
    for convo in conversations:
        convo.unread_count = convo.messages.filter(
            is_read=False
        ).exclude(sender=request.user).count()
    
    return render(request, 'marketplace/inbox.html', {'conversations': conversations})


@login_required
def conversation_detail(request, pk):
    """View a specific conversation"""
    conversation = get_object_or_404(Conversation, pk=pk)
    
    # Check if user is part of this conversation
    if request.user not in [conversation.buyer, conversation.seller]:
        messages.error(request, 'You do not have access to this conversation.')
        return redirect('inbox')
    
    # Mark messages as read
    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            
            # Update conversation timestamp
            conversation.save()  # This updates updated_at
            
            return redirect('conversation_detail', pk=pk)
    else:
        form = MessageForm()
    
    other_user = conversation.get_other_user(request.user)
    
    context = {
        'conversation': conversation,
        'messages': conversation.messages.all(),
        'form': form,
        'other_user': other_user,
    }
    return render(request, 'marketplace/conversation_detail.html', context)


@login_required
def start_conversation(request, pk):
    """Start a conversation about a book"""
    book = get_object_or_404(Book, pk=pk)
    
    if book.seller == request.user:
        messages.error(request, 'You cannot message yourself about your own listing.')
        return redirect('book_detail', pk=pk)
    
    # Check if conversation already exists
    conversation, created = Conversation.objects.get_or_create(
        buyer=request.user,
        seller=book.seller,
        book=book
    )
    
    if created:
        messages.success(request, 'Conversation started!')
    
    return redirect('conversation_detail', pk=conversation.pk)
