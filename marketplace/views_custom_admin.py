from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Avg
from marketplace.models import Book, Order, Payment, UserProfile
from django.utils import timezone
from datetime import timedelta

@staff_member_required
def admin_dashboard(request):
    """Admin-only dashboard overview"""
    # Key Statistics
    total_users = User.objects.count()
    total_books = Book.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(status='completed').aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Book Stats
    available_books = Book.objects.filter(status='available').count()
    sold_books = Book.objects.filter(status='sold').count()
    
    # Order Stats
    pending_orders = Order.objects.filter(status__in=['pending_payment', 'paid']).count()
    shipped_orders = Order.objects.filter(status='shipped').count()
    
    # Recent Activity
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_orders = Order.objects.order_by('-created_at')[:5]
    recent_books = Book.objects.order_by('-created_at')[:5]
    
    context = {
        'total_users': total_users,
        'total_books': total_books,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'available_books': available_books,
        'sold_books': sold_books,
        'pending_orders': pending_orders,
        'shipped_orders': shipped_orders,
        'recent_users': recent_users,
        'recent_orders': recent_orders,
        'recent_books': recent_books,
        'active_tab': 'dashboard'
    }
    return render(request, 'marketplace/admin_panel/dashboard.html', context)

@staff_member_required
def admin_user_list(request):
    """Manage site users"""
    users = User.objects.all().order_by('-date_joined')
    context = {
        'users': users,
        'active_tab': 'users'
    }
    return render(request, 'marketplace/admin_panel/user_list.html', context)

@staff_member_required
def admin_toggle_user_status(request, user_id):
    """Deactivate or activate a user account"""
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        if user != request.user: # Don't deactivate self
            user.is_active = not user.is_active
            user.save()
            from django.contrib import messages
            status = "activated" if user.is_active else "deactivated"
            messages.success(request, f"User {user.username} has been {status}.")
    return redirect('admin_user_list')

@staff_member_required
def admin_book_list(request):
    """Manage book listings"""
    books = Book.objects.all().order_by('-created_at')
    context = {
        'books': books,
        'active_tab': 'books'
    }
    return render(request, 'marketplace/admin_panel/book_list.html', context)

@staff_member_required
def admin_order_list(request):
    """Manage orders and payments"""
    orders = Order.objects.all().order_by('-created_at')
    context = {
        'orders': orders,
        'active_tab': 'orders'
    }
    return render(request, 'marketplace/admin_panel/order_list.html', context)
