from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
import json
import csv
from io import TextIOWrapper
from .models import Book, Order
from .forms import BookListingForm


@login_required
def analytics_dashboard(request):
    """Seller analytics dashboard"""
    # Get all seller's completed orders
    completed_orders = Order.objects.filter(
        seller=request.user,
        status='completed'
    )
    
    # Calculate stats
    stats = {
        'total_sales': completed_orders.count(),
        'total_revenue': completed_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0,
        'active_listings': Book.objects.filter(seller=request.user, status='available').count(),
        'avg_rating': request.user.seller_ratings_received.aggregate(Avg('rating'))['rating__avg'] or 0,
        'total_ratings': request.user.seller_ratings_received.count(),
    }
    
    # Sales over last 30 days for chart
    thirty_days_ago = timezone.now() - timedelta(days=30)
    chart_labels = []
    chart_data = []
    
    for i in range(30, -1, -1):
        date = timezone.now() - timedelta(days=i)
        date_str = date.strftime('%b %d')
        chart_labels.append(date_str)
        
        day_sales = completed_orders.filter(
            created_at__date=date.date()
        ).count()
        chart_data.append(day_sales)
    
    # Top selling books
    top_books = Book.objects.filter(
        seller=request.user
    ).annotate(
        sales_count=Count('orders', filter=Q(orders__status='completed')),
        total_revenue=Sum('orders__total_price', filter=Q(orders__status='completed')),
        avg_rating=Avg('reviews__rating')
    ).filter(sales_count__gt=0).order_by('-sales_count')[:5]
    
    # Category breakdown
    category_stats = completed_orders.values('book__category').annotate(
        count=Count('id')
    ).order_by('-count')[:6]
    
    category_labels = [dict(Book.CATEGORY_CHOICES).get(cat['book__category'], 'Unknown') 
                      for cat in category_stats]
    category_data = [cat['count'] for cat in category_stats]
    
    # Recent orders
    recent_orders = completed_orders.order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'category_labels': json.dumps(category_labels),
        'category_data': json.dumps(category_data),
        'top_books': top_books,
        'recent_orders': recent_orders,
    }
    
    return render(request, 'marketplace/analytics_dashboard.html', context)


@login_required
def bulk_upload(request):
    """Bulk upload books via CSV"""
    if request.method == 'POST':
        if 'csv_file' not in request.FILES:
            messages.error(request, 'Please select a CSV file.')
            return redirect('bulk_upload')
        
        csv_file = request.FILES['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return redirect('bulk_upload')
        
        try:
            # Read CSV file
            file_data = TextIOWrapper(csv_file.file, encoding='utf-8')
            csv_reader = csv.DictReader(file_data)
            
            created_count = 0
            error_count = 0
            errors = []
            
            for row_num, row in enumerate(csv_reader, start=2):
                try:
                    # Create book from CSV row
                    book = Book(
                        seller=request.user,
                        title=row.get('title', '').strip(),
                        author=row.get('author', '').strip(),
                        isbn=row.get('isbn', '').strip(),
                        publisher=row.get('publisher', '').strip(),
                        description=row.get('description', '').strip(),
                        price=float(row.get('price', 0)),
                        condition=row.get('condition', 'good'),
                        category=row.get('category', 'other'),
                        status='available'
                    )
                    book.full_clean()  # Validate
                    book.save()
                    created_count += 1
                    
                except Exception as e:
                    error_count += 1
                    errors.append(f'Row {row_num}: {str(e)}')
            
            # Show results
            if created_count > 0:
                messages.success(request, f'Successfully uploaded {created_count} books!')
            
            if error_count > 0:
                error_msg = f'{error_count} errors occurred. ' + ' | '.join(errors[:5])
                if len(errors) > 5:
                    error_msg += f' (and {len(errors) - 5} more...)'
                messages.warning(request, error_msg)
            
            return redirect('my_listings')
            
        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')
            return redirect('bulk_upload')
    
    return render(request, 'marketplace/bulk_upload.html')


def autocomplete_books(request):
    """AJAX endpoint for book search autocomplete"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    # Search in title, author, ISBN
    books = Book.objects.filter(
        Q(title__icontains=query) | 
        Q(author__icontains=query) |
        Q(isbn__icontains=query),
        status='available'
    ).distinct()[:10]
    
    suggestions = [
        {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'price': str(book.price),
            'url': f'/books/{book.id}/'
        }
        for book in books
    ]
    
    return JsonResponse({'suggestions': suggestions})
