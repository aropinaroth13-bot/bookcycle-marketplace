"""
Auto-initialization middleware for first deployment.
Automatically creates admin user and seeds database on first site visit.
"""
from django.contrib.auth.models import User
from marketplace.models import Book
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

class AutoInitMiddleware:
    """
    Middleware that runs one-time initialization on first request.
    Creates admin user and seeds demo data if database is empty.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self._initialized = False
    
    def __call__(self, request):
        # Only run once per application lifecycle
        if not self._initialized:
            self._initialize_database()
            self._initialized = True
        
        response = self.get_response(request)
        return response
    
    def _initialize_database(self):
        """Initialize database if it's empty"""
        try:
            # Check if database needs initialization
            book_count = Book.objects.count()
            admin_exists = User.objects.filter(is_superuser=True).exists()
            
            if book_count == 0 or not admin_exists:
                logger.info("🚀 First-time initialization detected! Setting up database...")
                
                # Run seed_data command
                call_command('seed_data')
                
                logger.info("✅ Database initialized successfully with demo data!")
            else:
                logger.info("✓ Database already initialized, skipping seed")
                
        except Exception as e:
            logger.warning(f"Auto-initialization failed (this is normal on first deploy): {str(e)}")
