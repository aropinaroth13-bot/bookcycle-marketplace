"""
One-time initialization view - visit this URL to seed the database.
No authentication required for first-time setup.
"""
from django.http import HttpResponse
from django.core.management import call_command
from marketplace.models import Book
from io import StringIO

def initialize_database(request):
    """
    Public URL to initialize database with demo data.
    After first run, this becomes admin-only.
    """
    # Check if already initialized
    book_count = Book.objects.count()
    
    if book_count > 0:
        return HttpResponse(f"""
            <h1>✅ Database Already Initialized!</h1>
            <p>Found {book_count} books in the database.</p>
            <p><a href="/">Go to Homepage</a></p>
        """)
    
    # Run seed command
    output = StringIO()
    try:
        call_command('seed_data', stdout=output)
        result = output.getvalue()
        return HttpResponse(f"""
            <h1>🎉 Database Initialized Successfully!</h1>
            <pre>{result}</pre>
            <p><strong>Admin Login:</strong></p>
            <ul>
                <li>Username: admin</li>
                <li>Password: Admin@123</li>
            </ul>
            <p><a href="/">Go to Homepage</a> | <a href="/admin">Admin Panel</a></p>
        """)
    except Exception as e:
        return HttpResponse(f"""
            <h1>❌ Initialization Failed</h1>
            <pre>Error: {str(e)}\n\n{output.getvalue()}</pre>
            <p><a href="/">Go to Homepage</a></p>
        """)
