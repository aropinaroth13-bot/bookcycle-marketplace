from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class UserProfile(models.Model):
    """Extended user profile with additional marketplace details"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class Book(models.Model):
    """Book listing model"""
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('acceptable', 'Acceptable'),
    ]
    
    CATEGORY_CHOICES = [
        ('fiction', 'Fiction'),
        ('non_fiction', 'Non-Fiction'),
        ('academic', 'Academic'),
        ('children', 'Children\'s Books'),
        ('comics', 'Comics & Graphic Novels'),
        ('biography', 'Biography'),
        ('science', 'Science & Technology'),
        ('history', 'History'),
        ('self_help', 'Self Help'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('pending', 'Pending'),
    ]
    
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='other')
    isbn = models.CharField(max_length=13, blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Images
    image1 = models.ImageField(upload_to='books/', blank=True, null=True)
    image2 = models.ImageField(upload_to='books/', blank=True, null=True)
    image3 = models.ImageField(upload_to='books/', blank=True, null=True)
    image4 = models.ImageField(upload_to='books/', blank=True, null=True)
    image5 = models.ImageField(upload_to='books/', blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    def get_primary_image(self):
        """Return the first available image"""
        for i in range(1, 6):
            img = getattr(self, f'image{i}')
            if img:
                return img
        return None
    
    def is_available(self):
        """Check if book is available for purchase"""
        return self.status == 'available'


class CartItem(models.Model):
    """Shopping cart items"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'book')
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.quantity}x {self.book.title} in {self.user.username}'s cart"
    
    def get_total_price(self):
        """Calculate total price for this cart item"""
        return self.book.price * self.quantity


class Order(models.Model):
    """Order model for tracking purchases"""
    STATUS_CHOICES = [
        ('pending_payment', 'Pending Payment'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_id = models.CharField(max_length=255, blank=True)
    payment_gateway = models.CharField(max_length=20, default='stripe')  # stripe or razorpay
    shipping_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id} - {self.book.title} by {self.buyer.username}"
    
    def mark_as_paid(self, payment_id):
        """Mark order as paid"""
        self.status = 'paid'
        self.payment_status = 'completed'
        self.payment_id = payment_id
        self.save()
    
    def mark_as_shipped(self):
        """Mark order as shipped"""
        self.status = 'shipped'
        self.save()
    
    def mark_as_completed(self):
        """Mark order as completed"""
        self.status = 'completed'
        self.save()
    
    def cancel_order(self):
        """Cancel the order"""
        self.status = 'cancelled'
        # Make book available again
        self.book.status = 'available'
        self.book.save()
        self.save()
    
    def process_refund(self):
        """Process refund for the order"""
        self.payment_status = 'refunded'
        # Make book available again
        self.book.status = 'available'
        self.book.save()
        self.save()


class Payment(models.Model):
    """Payment transaction records"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment_record')
    payment_id = models.CharField(max_length=255, unique=True)
    payment_method = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ], default='pending')
    payment_gateway = models.CharField(max_length=20, default='stripe')
    transaction_date = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(blank=True, null=True)  # Store additional payment gateway data
    
    def __str__(self):
        return f"Payment {self.payment_id} for Order #{self.order.id}"
    
    def verify_payment(self):
        """Verify payment status with payment gateway"""
        # This will be implemented when integrating with payment gateways
        pass


class BookReview(models.Model):
    """Book reviews and ratings"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    title = models.CharField(max_length=255)
    comment = models.TextField()
    verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('book', 'user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s review of {self.book.title} - {self.rating}★"


class SellerRating(models.Model):
    """Seller ratings from buyers"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='seller_rating')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_ratings_received')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_ratings_given')
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.buyer.username}'s rating of {self.seller.username} - {self.rating}★"


class Wishlist(models.Model):
    """User wishlist for books"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'book')
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.book.title} in {self.user.username}'s wishlist"


class Conversation(models.Model):
    """Conversation between buyer and seller"""
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_conversations')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_conversations')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('buyer', 'seller', 'book')
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Conversation about {self.book.title} between {self.buyer.username} and {self.seller.username}"
    
    def get_other_user(self, user):
        """Get the other user in the conversation"""
        return self.seller if user == self.buyer else self.buyer


class Message(models.Model):
    """Individual message in a conversation"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} at {self.created_at}"

