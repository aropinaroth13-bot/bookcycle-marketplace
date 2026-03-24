from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Book, UserProfile, BookReview, Message


class UserRegistrationForm(UserCreationForm):
    """Extended user registration form"""
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'phone_number', 'address']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data.get('phone_number', ''),
                address=self.cleaned_data.get('address', '')
            )
        return user


class UserProfileForm(forms.ModelForm):
    """User profile editing form"""
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address', 'profile_picture']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            # Update user fields
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()
            profile.save()
        return profile


class BookListingForm(forms.ModelForm):
    """Form for creating and editing book listings"""
    class Meta:
        model = Book
        fields = [
            'title', 'author', 'description', 'price', 'quantity', 'condition', 
            'category', 'isbn', 'publisher', 'image1', 'image2', 
            'image3', 'image4', 'image5'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make images optional
        for i in range(1, 6):
            self.fields[f'image{i}'].required = False


class BookSearchForm(forms.Form):
    """Search and filter form for books"""
    query = forms.CharField(max_length=255, required=False, 
                           widget=forms.TextInput(attrs={'placeholder': 'Search by title or author...'}))
    category = forms.ChoiceField(choices=[('', 'All Categories')] + Book.CATEGORY_CHOICES, required=False)
    condition = forms.ChoiceField(choices=[('', 'All Conditions')] + Book.CONDITION_CHOICES, required=False)
    min_price = forms.DecimalField(max_digits=10, decimal_places=2, required=False,
                                   widget=forms.NumberInput(attrs={'placeholder': 'Min Price'}))
    max_price = forms.DecimalField(max_digits=10, decimal_places=2, required=False,
                                   widget=forms.NumberInput(attrs={'placeholder': 'Max Price'}))
    sort_by = forms.ChoiceField(choices=[
        ('newest', 'Newest First'),
        ('price_low', 'Price: Low to High'),
        ('price_high', 'Price: High to Low'),
    ], required=False)


class CheckoutForm(forms.Form):
    """Checkout form for order placement"""
    shipping_address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter complete shipping address'}),
        required=True
    )
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'placeholder': 'Contact number'}),
        required=True
    )


class BookReviewForm(forms.ModelForm):
    """Form for submitting book reviews"""
    RATING_CHOICES = [(i, '⭐' * i) for i in range(1, 6)]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )
    
    class Meta:
        model = BookReview
        fields = ['rating', 'title', 'comment']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Summary of your review'}),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your thoughts about this book...'}),
        }


class MessageForm(forms.ModelForm):
    """Form for sending messages"""
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Type your message...',
                'class': 'message-input'
            }),
        }

