"""
Integration tests for BOOKCYCLE views
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from marketplace.models import Book, CartItem, Order
from decimal import Decimal


class HomePageTest(TestCase):
    """Test home page"""
    
    def setUp(self):
        self.client = Client()
    
    def test_home_page_loads(self):
        """Test home page returns 200"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'BOOKCYCLE')


class UserAuthenticationTest(TestCase):
    """Test user registration and login"""
    
    def setUp(self):
        self.client = Client()
    
    def test_registration_page_loads(self):
        """Test registration page loads"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
    
    def test_user_registration(self):
        """Test user can register"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123!',
            'password2': 'testpass123!',
        })
        # Should redirect after successful registration
        self.assertEqual(response.status_code, 302)
        # User should be created
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_login_page_loads(self):
        """Test login page loads"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
    
    def test_user_login(self):
        """Test user can login"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)


class BookListingTest(TestCase):
    """Test book listing functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='seller',
            email='seller@example.com',
            password='testpass123'
        )
        self.book = Book.objects.create(
            seller=self.user,
            title='Test Book',
            author='Test Author',
            price=Decimal('199.99'),
            condition='good',
            category='fiction',
            description='Test description'
        )
    
    def test_browse_books_page(self):
        """Test books page loads"""
        response = self.client.get(reverse('browse_books'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Book')
    
    def test_book_detail_page(self):
        """Test book detail page loads"""
        response = self.client.get(reverse('book_detail', args=[self.book.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Book')
        self.assertContains(response, 'Test Author')
    
    def test_create_listing_requires_login(self):
        """Test creating listing requires login"""
        response = self.client.get(reverse('create_listing'))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_create_listing_authenticated(self):
        """Test logged in user can access create listing"""
        self.client.login(username='seller', password='testpass123')
        response = self.client.get(reverse('create_listing'))
        self.assertEqual(response.status_code, 200)


class ShoppingCartTest(TestCase):
    """Test shopping cart functionality"""
    
    def setUp(self):
        self.client = Client()
        self.buyer = User.objects.create_user(
            username='buyer',
            email='buyer@example.com',
            password='testpass123'
        )
        self.seller = User.objects.create_user(
            username='seller',
            email='seller@example.com',
            password='testpass123'
        )
        self.book = Book.objects.create(
            seller=self.seller,
            title='Cart Test Book',
            author='Author',
            price=Decimal('100.00'),
            condition='good',
            category='fiction'
        )
    
    def test_add_to_cart_requires_login(self):
        """Test adding to cart requires login"""
        response = self.client.get(reverse('add_to_cart', args=[self.book.id]))
        self.assertEqual(response.status_code, 302)
    
    def test_add_to_cart_authenticated(self):
        """Test logged in user can add to cart"""
        self.client.login(username='buyer', password='testpass123')
        response = self.client.get(reverse('add_to_cart', args=[self.book.id]))
        # Should redirect after adding
        self.assertEqual(response.status_code, 302)
        # Cart item should be created
        self.assertTrue(CartItem.objects.filter(user=self.buyer, book=self.book).exists())
    
    def test_view_cart(self):
        """Test viewing cart"""
        self.client.login(username='buyer', password='testpass123')
        CartItem.objects.create(user=self.buyer, book=self.book, quantity=1)
        response = self.client.get(reverse('view_cart'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cart Test Book')


class ReviewTest(TestCase):
    """Test review functionality"""
    
    def setUp(self):
        self.client = Client()
        self.reviewer = User.objects.create_user(
            username='reviewer',
            email='reviewer@example.com',
            password='testpass123'
        )
        self.seller = User.objects.create_user(
            username='seller',
            email='seller@example.com',
            password='testpass123'
        )
        self.book = Book.objects.create(
            seller=self.seller,
            title='Review Test Book',
            author='Author',
            price=Decimal('200.00'),
            condition='good',
            category='fiction'
        )
    
    def test_submit_review_requires_login(self):
        """Test submitting review requires login"""
        response = self.client.get(reverse('submit_review', args=[self.book.id]))
        self.assertEqual(response.status_code, 302)
    
    def test_submit_review_page_loads(self):
        """Test review page loads for logged in user"""
        self.client.login(username='reviewer', password='testpass123')
        response = self.client.get(reverse('submit_review', args=[self.book.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_book_reviews_page(self):
        """Test book reviews page loads"""
        response = self.client.get(reverse('book_reviews', args=[self.book.id]))
        self.assertEqual(response.status_code, 200)


class WishlistTest(TestCase):
    """Test wishlist functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='testpass123'
        )
        self.seller = User.objects.create_user(
            username='seller',
            email='seller@example.com',
            password='testpass123'
        )
        self.book = Book.objects.create(
            seller=self.seller,
            title='Wishlist Book',
            author='Author',
            price=Decimal('150.00'),
            condition='like_new',
            category='non_fiction'
        )
    
    def test_wishlist_requires_login(self):
        """Test wishlist requires login"""
        response = self.client.get(reverse('wishlist'))
        self.assertEqual(response.status_code, 302)
    
    def test_add_to_wishlist(self):
        """Test adding to wishlist"""
        self.client.login(username='user', password='testpass123')
        response = self.client.get(reverse('add_to_wishlist', args=[self.book.id]))
        self.assertEqual(response.status_code, 302)
    
    def test_view_wishlist(self):
        """Test viewing wishlist"""
        self.client.login(username='user', password='testpass123')
        response = self.client.get(reverse('wishlist'))
        self.assertEqual(response.status_code, 200)


class MessagingTest(TestCase):
    """Test messaging functionality"""
    
    def setUp(self):
        self.client = Client()
        self.buyer = User.objects.create_user(
            username='buyer',
            email='buyer@example.com',
            password='testpass123'
        )
        self.seller = User.objects.create_user(
            username='seller',
            email='seller@example.com',
            password='testpass123'
        )
        self.book = Book.objects.create(
            seller=self.seller,
            title='Message Book',
            author='Author',
            price=Decimal('250.00'),
            condition='very_good',
            category='fiction'
        )
    
    def test_inbox_requires_login(self):
        """Test inbox requires login"""
        response = self.client.get(reverse('inbox'))
        self.assertEqual(response.status_code, 302)
    
    def test_inbox_page_loads(self):
        """Test inbox loads for logged in user"""
        self.client.login(username='buyer', password='testpass123')
        response = self.client.get(reverse('inbox'))
        self.assertEqual(response.status_code, 200)
    
    def test_start_conversation(self):
        """Test starting a conversation"""
        self.client.login(username='buyer', password='testpass123')
        response = self.client.get(reverse('start_conversation', args=[self.book.id]))
        # Should redirect to conversation
        self.assertEqual(response.status_code, 302)
