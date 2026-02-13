from django.http import HttpResponse
from django.core.management import call_command
from django.contrib.admin.views.decorators import staff_member_required
from io import StringIO

@staff_member_required
def seed_database(request):
    """
    Admin-only view to seed the database with demo data.
    Access this URL after logging in as admin to populate the database.
    """
    output = StringIO()
    try:
        call_command('seed_data', stdout=output)
        return HttpResponse(f'<pre>{output.getvalue()}</pre>')
    except Exception as e:
        return HttpResponse(f'<pre>Error: {str(e)}\n\n{output.getvalue()}</pre>')
