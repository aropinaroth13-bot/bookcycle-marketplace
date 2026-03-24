from django.contrib import admin
from .models import UserProfile, Book, CartItem, Order, Payment, BookReview, SellerRating, Wishlist, Conversation, Message


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone_number']
    list_filter = ['created_at']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'price', 'quantity', 'condition', 'category', 'status', 'seller', 'created_at']
    list_filter = ['status', 'condition', 'category', 'created_at']
    search_fields = ['title', 'author', 'isbn', 'seller__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Book Information', {
            'fields': ('title', 'author', 'description', 'isbn', 'publisher')
        }),
        ('Pricing & Condition', {
            'fields': ('price', 'quantity', 'condition', 'category', 'status')
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
    list_display = ['id', 'buyer', 'seller', 'book', 'total_price', 'status', 'payment_status', 'tracking_status', 'created_at']
    list_filter = ['status', 'payment_status', 'payment_gateway', 'courier_service', 'created_at', 'shipped_date']
    search_fields = ['buyer__username', 'seller__username', 'book__title', 'payment_id', 'tracking_number']
    readonly_fields = ['created_at', 'updated_at', 'shipped_date', 'delivered_date']
    list_per_page = 50
    date_hierarchy = 'created_at'
    
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
        ('Shipping Address', {
            'fields': ('shipping_address',)
        }),
        ('📦 Tracking Information', {
            'fields': ('tracking_number', 'courier_service', 'estimated_delivery_date', 'shipped_date', 'delivered_date'),
            'classes': ('collapse',),
            'description': 'Delivery tracking details'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_shipped', 'mark_as_completed', 'mark_as_delivered', 'export_as_csv']
    
    def tracking_status(self, obj):
        """Display tracking status in list"""
        if obj.tracking_number:
            return f"✅ {obj.get_courier_service_display()}"
        return "❌ No tracking"
    tracking_status.short_description = "Tracking"
    
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f'{updated} order(s) marked as shipped.')
    mark_as_shipped.short_description = "Mark selected orders as shipped"
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} order(s) marked as completed.')
    mark_as_completed.short_description = "Mark selected orders as completed"
    
    def mark_as_delivered(self, request, queryset):
        from django.utils import timezone
        for order in queryset:
            order.mark_as_delivered()
        self.message_user(request, f'{queryset.count()} order(s) marked as delivered.')
    mark_as_delivered.short_description = "Mark selected orders as delivered"
    
    def export_as_csv(self, request, queryset):
        """Export selected orders as CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Buyer', 'Seller', 'Book', 'Price', 'Status', 'Payment Status', 
                        'Tracking Number', 'Courier', 'Created', 'Shipped'])
        
        for order in queryset:
            writer.writerow([
                order.id,
                order.buyer.username,
                order.seller.username,
                order.book.title,
                order.total_price,
                order.get_status_display(),
                order.get_payment_status_display(),
                order.tracking_number or 'N/A',
                order.get_courier_service_display() if order.courier_service else 'N/A',
                order.created_at.strftime('%Y-%m-%d %H:%M'),
                order.shipped_date.strftime('%Y-%m-%d %H:%M') if order.shipped_date else 'N/A'
            ])
        
        return response
    export_as_csv.short_description = "Export selected orders as CSV"


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

