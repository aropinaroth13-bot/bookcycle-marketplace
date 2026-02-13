from django.contrib import admin
from .models import UserProfile, Book, CartItem, Order, Payment, BookReview, SellerRating, Wishlist, Conversation, Message


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone_number']
    list_filter = ['created_at']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'price', 'condition', 'category', 'status', 'seller', 'created_at']
    list_filter = ['status', 'condition', 'category', 'created_at']
    search_fields = ['title', 'author', 'isbn', 'seller__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Book Information', {
            'fields': ('title', 'author', 'description', 'isbn', 'publisher')
        }),
        ('Pricing & Condition', {
            'fields': ('price', 'condition', 'category', 'status')
        }),
        ('Seller', {
            'fields': ('seller',)
        }),
        ('Images', {
            'fields': ('image1', 'image2', 'image3', 'image4', 'image5')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'quantity', 'added_at']
    search_fields = ['user__username', 'book__title']
    list_filter = ['added_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'seller', 'book', 'total_price', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'payment_gateway', 'created_at']
    search_fields = ['buyer__username', 'seller__username', 'book__title', 'payment_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Order Details', {
            'fields': ('buyer', 'seller', 'book', 'quantity', 'total_price')
        }),
        ('Status', {
            'fields': ('status', 'payment_status')
        }),
        ('Payment', {
            'fields': ('payment_id', 'payment_gateway')
        }),
        ('Shipping', {
            'fields': ('shipping_address',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_shipped', 'mark_as_completed']
    
    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
    mark_as_shipped.short_description = "Mark selected orders as shipped"
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = "Mark selected orders as completed"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'order', 'amount', 'status', 'payment_gateway', 'transaction_date']
    list_filter = ['status', 'payment_gateway', 'transaction_date']
    search_fields = ['payment_id', 'order__id']
    readonly_fields = ['transaction_date']


@admin.register(BookReview)
class BookReviewAdmin(admin.ModelAdmin):
    list_display = ['book', 'user', 'rating', 'title', 'verified_purchase', 'created_at']
    list_filter = ['rating', 'verified_purchase', 'created_at']
    search_fields = ['book__title', 'user__username', 'title', 'comment']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SellerRating)
class SellerRatingAdmin(admin.ModelAdmin):
    list_display = ['seller', 'buyer', 'rating', 'order', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['seller__username', 'buyer__username']
    readonly_fields = ['created_at']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'added_at']
    search_fields = ['user__username', 'book__title']
    list_filter = ['added_at']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'seller', 'book', 'created_at', 'updated_at']
    search_fields = ['buyer__username', 'seller__username', 'book__title']
    list_filter = ['created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'sender', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'content']
    readonly_fields = ['created_at']

