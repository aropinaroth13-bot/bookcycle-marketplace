"""
Unit tests for BOOKCYCLE models
"""
from django.test import TestCase
from django.contrib.auth.models import User
from marketplace.models import Book, UserProfile, CartItem, Order, BookReview, Wishlist, Conversation, Message
from decimal import Decimal


class UserProfileModelTest(TestCase):
    """Test UserProfile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_profile_creation(self):
        """Test that profile is automatically created with user"""
        self.assertTrue(hasattr(self.user, 'userprofile'))
        self.assertEqual(self.user.userprofile.user, self.user)
    
    def test_user_profile_str(self):
        """Test string representation"""
        self.assertEqual(str(self.user.userprofile), 'testuser')


class BookModelTest(TestCase):
    """Test Book model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='seller',
            email='seller@example.com',
            password='testpass123'
        )
        self.book = Book.objects.create(
            seller=self.user,
            title='Test Book',
            author='Test Author',
            isbn='1234567890123',
            price=Decimal('299.99'),
            condition='good',
            category='fiction',
            description='A test book description'
        )
    
    def test_book_creation(self):
        """Test book is created correctly"""
        self.assertEqual(self.book.title, 'Test Book')
        self.assertEqual(self.book.author, 'Test Author')
        self.assertEqual(self.book.price, Decimal('299.99'))
        self.assertEqual(self.book.status, 'available')  # default status
    
    def test_book_str(self):
        """Test string representation"""
        self.assertEqual(str(self.book), 'Test Book by Test Author')
    
    def test_is_available(self):
        """Test availability check"""
        self.assertTrue(self.book.is_available())
        self.book.status = 'sold'
        self.assertFalse(self.book.is_available())


class CartItemModelTest(TestCase):
    """Test CartItem model"""
    
    def setUp(self):
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
        self.cart_item = CartItem.objects.create(
            user=self.buyer,
            book=self.book,
            quantity=2
        )
    
    def test_cart_item_creation(self):
        """Test cart item is created"""
        self.assertEqual(self.cart_item.user, self.buyer)
        self.assertEqual(self.cart_item.book, self.book)
        self.assertEqual(self.cart_item.quantity, 2)
    
    def test_get_total_price(self):
        """Test total price calculation"""
        expected_total = self.book.price * 2
        self.assertEqual(self.cart_item.get_total_price(), expected_total)


class OrderModelTest(TestCase):
    """Test Order model"""
    
    def setUp(self):
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
            title='Order Test Book',
            author='Author',
            price=Decimal('500.00'),
            condition='new',
            category='textbook'
        )
        self.order = Order.objects.create(
            buyer=self.buyer,
            seller=self.seller,
            book=self.book,
            quantity=1,
            total_price=Decimal('500.00'),
            shipping_address='123 Test St, Test City'
        )
    
    def test_order_creation(self):
        """Test order is created with correct status"""
        self.assertEqual(self.order.status, 'pending_payment')
        self.assertEqual(self.order.total_price, Decimal('500.00'))
    
    def test_mark_as_paid(self):
        """Test marking order as paid"""
        self.order.mark_as_paid('payment_intent_123')
        self.assertEqual(self.order.status, 'paid')
        self.assertEqual(self.order.payment_id, 'payment_intent_123')


class BookReviewModelTest(TestCase):
    """Test BookReview model"""
    
    def setUp(self):
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
        self.review = BookReview.objects.create(
            book=self.book,
            user=self.reviewer,
            rating=4,
            title='Great book!',
            comment='Really enjoyed this book.',
            verified_purchase=True
        )
    
    def test_review_creation(self):
        """Test review is created"""
        self.assertEqual(self.review.rating, 4)
        self.assertTrue(self.review.verified_purchase)
    
    def test_review_unique_constraint(self):
        """Test one review per user per book"""
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            BookReview.objects.create(
                book=self.book,
                user=self.reviewer,
                rating=5,
                title='Another review',
                comment='This should fail'
            )


class WishlistModelTest(TestCase):
    """Test Wishlist model"""
    
    def setUp(self):
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
        self.wishlist_item = Wishlist.objects.create(
            user=self.user,
            book=self.book
        )
    
    def test_wishlist_creation(self):
        """Test wishlist item is created"""
        self.assertEqual(self.wishlist_item.user, self.user)
        self.assertEqual(self.wishlist_item.book, self.book)
        self.assertIsNotNone(self.wishlist_item.added_at)
    
    def test_wishlist_unique_constraint(self):
        """Test one wishlist entry per user per book"""
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Wishlist.objects.create(
                user=self.user,
                book=self.book
            )


class ConversationModelTest(TestCase):
    """Test Conversation model"""
    
    def setUp(self):
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
            title='Conversation Book',
            author='Author',
            price=Decimal('300.00'),
            condition='good',
            category='textbook'
        )
        self.conversation = Conversation.objects.create(
            buyer=self.buyer,
            seller=self.seller,
            book=self.book
        )
    
    def test_conversation_creation(self):
        """Test conversation is created"""
        self.assertEqual(self.conversation.buyer, self.buyer)
        self.assertEqual(self.conversation.seller, self.seller)
        self.assertEqual(self.conversation.book, self.book)
    
    def test_get_other_user(self):
        """Test getting the other user in conversation"""
        self.assertEqual(self.conversation.get_other_user(self.buyer), self.seller)
        self.assertEqual(self.conversation.get_other_user(self.seller), self.buyer)


class MessageModelTest(TestCase):
    """Test Message model"""
    
    def setUp(self):
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
        self.conversation = Conversation.objects.create(
            buyer=self.buyer,
            seller=self.seller,
            book=self.book
        )
        self.message = Message.objects.create(
            conversation=self.conversation,
            sender=self.buyer,
            content='Hello, is this book still available?'
        )
    
    def test_message_creation(self):
        """Test message is created"""
        self.assertEqual(self.message.sender, self.buyer)
        self.assertFalse(self.message.is_read)
        self.assertIsNotNone(self.message.created_at)
    
    def test_message_str(self):
        """Test string representation"""
        expected = f"Message from {self.buyer.username} in conversation {self.conversation.id}"
        self.assertEqual(str(self.message), expected)
