from django.urls import path
from . import views
from . import advanced_views
from . import views_admin

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Book Listings
    path('books/', views.browse_books, name='browse_books'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('listings/create/', views.create_listing, name='create_listing'),
    path('listings/<int:pk>/edit/', views.edit_listing, name='edit_listing'),
    path('listings/<int:pk>/delete/', views.delete_listing, name='delete_listing'),
    path('my-listings/', views.my_listings, name='my_listings'),
    
    # Shopping Cart
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:pk>/', views.update_cart, name='update_cart'),
    
    # Checkout and Orders
    path('checkout/', views.checkout, name='checkout'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('my-sales/', views.my_sales, name='my_sales'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/cancel/', views.cancel_order, name='cancel_order'),
    path('orders/<int:pk>/update-tracking/', views.update_order_tracking, name='update_order_tracking'),
    
    # Advanced Features
    path('analytics/', advanced_views.analytics_dashboard, name='analytics_dashboard'),
    path('bulk-upload/', advanced_views.bulk_upload, name='bulk_upload'),
    path('api/autocomplete/', advanced_views.autocomplete_books, name='autocomplete_books'),
    
    # Payment
    path('payment/process/', views.process_payment, name='process_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancelled/', views.payment_cancelled, name='payment_cancelled'),
    path('payment/razorpay/callback/', views.razorpay_callback, name='razorpay_callback'),
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
    
    # Reviews
    path('books/<int:pk>/review/', views.submit_review, name='submit_review'),
    path('books/<int:pk>/reviews/', views.book_reviews, name='book_reviews'),
    
    # Wishlist
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:pk>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:pk>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # Messaging
    path('inbox/', views.inbox, name='inbox'),
    path('conversation/<int:pk>/', views.conversation_detail, name='conversation_detail'),
    path('conversation/start/<int:pk>/', views.start_conversation, name='start_conversation'),
    
    # Admin utilities
    path('initialize/', views_admin.initialize_database, name='initialize_database'),
]
