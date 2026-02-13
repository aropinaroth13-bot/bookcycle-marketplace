from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from marketplace.models import Book, UserProfile, BookImage
from decimal import Decimal
from django.core.files.base import ContentFile
import random
import requests
from io import BytesIO


class Command(BaseCommand):
    help = 'Seed the database with demo users and books'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')

        # Create demo users
        users_data = [
            {'username': 'john_doe', 'email': 'john@example.com', 'password': 'Demo@123', 'first_name': 'John', 'last_name': 'Doe'},
            {'username': 'jane_smith', 'email': 'jane@example.com', 'password': 'Demo@123', 'first_name': 'Jane', 'last_name': 'Smith'},
            {'username': 'mike_wilson', 'email': 'mike@example.com', 'password': 'Demo@123', 'first_name': 'Mike', 'last_name': 'Wilson'},
            {'username': 'sarah_jones', 'email': 'sarah@example.com', 'password': 'Demo@123', 'first_name': 'Sarah', 'last_name': 'Jones'},
            {'username': 'admin', 'email': 'admin@bookcycle.com', 'password': 'Admin@123', 'first_name': 'Admin', 'last_name': 'User', 'is_staff': True, 'is_superuser': True},
        ]

        users = []
        for user_data in users_data:
            if not User.objects.filter(username=user_data['username']).exists():
                is_staff = user_data.pop('is_staff', False)
                is_superuser = user_data.pop('is_superuser', False)
                password = user_data.pop('password')
                
                user = User.objects.create_user(**user_data)
                user.is_staff = is_staff
                user.is_superuser = is_superuser
                user.set_password(password)
                user.save()
                
                # Create user profile
                UserProfile.objects.create(
                    user=user,
                    phone_number=f'+91 9{random.randint(100000000, 999999999)}',
                    address=f'{random.randint(1, 999)} Sample Street, City, State, {random.randint(100000, 999999)}'
                )
                users.append(user)
                self.stdout.write(self.style.SUCCESS(f'Created user: {user.username}'))
            else:
                users.append(User.objects.get(username=user_data['username']))
                self.stdout.write(f'User already exists: {user_data["username"]}')

        # Create demo books
        books_data = [
            {'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 'description': 'A classic American novel set in the Jazz Age', 'category': 'fiction', 'condition': 'good', 'isbn': '9780743273565', 'publisher': 'Scribner'},
            {'title': 'To Kill a Mockingbird', 'author': 'Harper Lee', 'description': 'A gripping tale of racial injustice and childhood innocence', 'category': 'fiction', 'condition': 'like_new', 'isbn': '9780061120084', 'publisher': 'Harper Perennial'},
            {'title': '1984', 'author': 'George Orwell', 'description': 'A dystopian social science fiction novel and cautionary tale', 'category': 'fiction', 'condition': 'good', 'isbn': '9780451524935', 'publisher': 'Signet Classic'},
            {'title': 'Pride and Prejudice', 'author': 'Jane Austen', 'description': 'A romantic novel of manners', 'category': 'fiction', 'condition': 'acceptable', 'isbn': '9780141439518', 'publisher': 'Penguin Classics'},
            {'title': 'The Catcher in the Rye', 'author': 'J.D. Salinger', 'description': 'A story about teenage rebellion and angst', 'category': 'fiction', 'condition': 'new', 'isbn': '9780316769174', 'publisher': 'Little Brown'},
            
            {'title': 'Sapiens', 'author': 'Yuval Noah Harari', 'description': 'A brief history of humankind', 'category': 'non_fiction', 'condition': 'like_new', 'isbn': '9780062316110', 'publisher': 'Harper'},
            {'title': 'Educated', 'author': 'Tara Westover', 'description': 'A memoir about a young woman who grows up in a strict family', 'category': 'biography', 'condition': 'good', 'isbn': '9780399590504', 'publisher': 'Random House'},
            {'title': 'Becoming', 'author': 'Michelle Obama', 'description': 'A memoir by the former First Lady of the United States', 'category': 'biography', 'condition': 'new', 'isbn': '9781524763138', 'publisher': 'Crown'},
            
            {'title': 'Introduction to Algorithms', 'author': 'Thomas H. Cormen', 'description': 'Comprehensive textbook on algorithms', 'category': 'academic', 'condition': 'good', 'isbn': '9780262033848', 'publisher': 'MIT Press'},
            {'title': 'Clean Code', 'author': 'Robert C. Martin', 'description': 'A handbook of agile software craftsmanship', 'category': 'science', 'condition': 'like_new', 'isbn': '9780132350884', 'publisher': 'Prentice Hall'},
            {'title': 'The Pragmatic Programmer', 'author': 'Andrew Hunt', 'description': 'From journeyman to master', 'category': 'science', 'condition': 'good', 'isbn': '9780135957059', 'publisher': 'Addison-Wesley'},
            
            {'title': 'Harry Potter and the Philosopher\'s Stone', 'author': 'J.K. Rowling', 'description': 'The first book in the Harry Potter series', 'category': 'fiction', 'condition': 'acceptable', 'isbn': '9780439708180', 'publisher': 'Scholastic'},
            {'title': 'The Hobbit', 'author': 'J.R.R. Tolkien', 'description': 'A fantasy novel and children\'s book', 'category': 'fiction', 'condition': 'good', 'isbn': '9780547928227', 'publisher': 'Houghton Mifflin'},
            {'title': 'Matilda', 'author': 'Roald Dahl', 'description': 'A children\'s novel about a young prodigy', 'category': 'children', 'condition': 'like_new', 'isbn': '9780142410370', 'publisher': 'Puffin Books'},
            {'title': 'Charlotte\'s Web', 'author': 'E.B. White', 'description': 'A classic children\'s novel', 'category': 'children', 'condition': 'good', 'isbn': '9780064400558', 'publisher': 'HarperCollins'},
            
            {'title': 'Watchmen', 'author': 'Alan Moore', 'description': 'A groundbreaking graphic novel', 'category': 'comics', 'condition': 'like_new', 'isbn': '9781401245252', 'publisher': 'DC Comics'},
            {'title': 'The Sandman Vol. 1', 'author': 'Neil Gaiman', 'description': 'A dark fantasy graphic novel series', 'category': 'comics', 'condition': 'new', 'isbn': '9781401284770', 'publisher': 'DC Comics'},
            
            {'title': 'Atomic Habits', 'author': 'James Clear', 'description': 'An easy way to build good habits and break bad ones', 'category': 'self_help', 'condition': 'new', 'isbn': '9780735211292', 'publisher': 'Avery'},
            {'title': 'The Power of Now', 'author': 'Eckhart Tolle', 'description': 'A guide to spiritual enlightenment', 'category': 'self_help', 'condition': 'good', 'isbn': '9781577314806', 'publisher': 'New World Library'},
            
            {'title': 'A Brief History of Time', 'author': 'Stephen Hawking', 'description': 'From the Big Bang to black holes', 'category': 'science', 'condition': 'acceptable', 'isbn': '9780553380163', 'publisher': 'Bantam'},
        ]

        prices = [199, 299, 399, 499, 599, 699, 799, 899, 999, 1299, 1499, 1999]
        
        for idx, book_data in enumerate(books_data, 1):
            if not Book.objects.filter(title=book_data['title'], author=book_data['author']).exists():
                # Randomly assign to a seller (not admin)
                seller = random.choice(users[:4])
                price = Decimal(random.choice(prices))
                
                book = Book.objects.create(
                    seller=seller,
                    price=price,
                    **book_data
                )
                
                # Add book cover image using placeholder service
                try:
                    # Use a book cover placeholder service with book number
                    colors = ['667eea', '764ba2', 'f093fb', '4facfe', 'fa709a', 'fee140', '30cfd0', 'a8edea']
                    color = random.choice(colors)
                    
                    # Create a nice book cover placeholder
                    image_url = f'https://via.placeholder.com/400x600/{color}/ffffff?text={book.title[:20].replace(" ", "+")}'
                    
                    response = requests.get(image_url, timeout=10)
                    if response.status_code == 200:
                        image_content = ContentFile(response.content)
                        book_image = BookImage.objects.create(book=book, is_primary=True)
                        book_image.image.save(f'{book.title[:30].replace(" ", "_")}.jpg', image_content, save=True)
                        self.stdout.write(self.style.SUCCESS(f'✓ Created book with image: {book_data["title"]}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'✓ Created book (no image): {book_data["title"]}'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'✓ Created book (image failed): {book_data["title"]} - {str(e)}'))
            else:
                self.stdout.write(f'Book already exists: {book_data["title"]}')

        self.stdout.write(self.style.SUCCESS('\nDatabase seeded successfully!'))
        self.stdout.write(self.style.SUCCESS('\nDemo Credentials:'))
        self.stdout.write('Admin: username=admin, password=Admin@123')
        self.stdout.write('Users: username=john_doe (or jane_smith, mike_wilson, sarah_jones), password=Demo@123')
