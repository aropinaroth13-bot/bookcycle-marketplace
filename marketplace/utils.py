"""
Utility functions for tracking user activity and advanced features
"""
from .models import Book
from django.core.cache import cache


def get_recently_viewed_books(request):
    """Get recently viewed books from session"""
    if request.user.is_authenticated:
        # For authenticated users, use session
        recently_viewed = request.session.get('recently_viewed', [])
        # Get actual book objects
        books = []
        for book_id in recently_viewed[:6]:  # Limit to 6
            try:
                book = Book.objects.get(pk=book_id, status='available')
                books.append(book)
            except Book.DoesNotExist:
                pass
        return books
    return []


def add_to_recently_viewed(request, book_id):
    """Add book to recently viewed list"""
    if request.user.is_authenticated:
        recently_viewed = request.session.get('recently_viewed', [])
        
        # Remove if already exists (to move to front)
        if book_id in recently_viewed:
            recently_viewed.remove(book_id)
        
        # Add to front
        recently_viewed.insert(0, book_id)
        
        # Keep only last 10
        recently_viewed = recently_viewed[:10]
        
        request.session['recently_viewed'] = recently_viewed
        request.session.modified = True


def get_recommended_books(user, limit=6):
    """Get recommended books based on user's wishlist and purchases"""
    if not user.is_authenticated:
        # For anonymous users, just return popular books
        return Book.objects.filter(status='available').order_by('-created_at')[:limit]
    
    # Get user's wishlist and purchase categories
    wishlist_categories = user.wishlist_items.values_list('book__category', flat=True)
    purchase_categories = user.purchases.values_list('book__category', flat=True)
    
    # Combine and get unique categories
    user_categories = set(list(wishlist_categories) + list(purchase_categories))
    
    if user_categories:
        # Recommend books from similar categories that user doesn't own
        recommended = Book.objects.filter(
            category__in=user_categories,
            status='available'
        ).exclude(
            seller=user
        ).exclude(
            id__in=user.wishlist_items.values_list('book_id', flat=True)
        ).order_by('-created_at')[:limit]
        
        return recommended
    
    # Fallback to latest books
    return Book.objects.filter(status='available').exclude(seller=user).order_by('-created_at')[:limit]


def get_book_stats(book):
    """Get statistics for a book"""
    reviews = book.reviews.all()
    total_reviews = reviews.count()
    
    if total_reviews > 0:
        total_rating = sum(r.rating for r in reviews)
        average_rating = total_rating / total_reviews
        
        # Rating distribution
        rating_distribution = {i: 0 for i in range(1, 6)}
        for review in reviews:
            rating_distribution[review.rating] += 1
    else:
        average_rating = 0
        rating_distribution = {i: 0 for i in range(1, 6)}
    
    return {
        'total_reviews': total_reviews,
        'average_rating': average_rating,
        'rating_distribution': rating_distribution,
    }


def get_seller_stats(seller):
    """Get statistics for a seller"""
    total_sales = seller.sales.filter(status='completed').count()
    total_listings = seller.books.count()
    available_listings = seller.books.filter(status='available').count()
    
    # Get average seller rating
    ratings = seller.seller_ratings_received.all()
    if ratings.exists():
        avg_rating = sum(r.rating for r in ratings) / ratings.count()
    else:
        avg_rating = 0
    
    return {
        'total_sales': total_sales,
        'total_listings': total_listings,
        'available_listings': available_listings,
        'average_rating': avg_rating,
        'total_ratings': ratings.count(),
    }
