from django import forms
from .models import Order


class TrackingUpdateForm(forms.Form):
    """Form for updating order tracking information"""
    tracking_number = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter tracking number',
            'class': 'form-control'
        })
    )
    courier_service = forms.ChoiceField(
        choices=[
            ('', 'Select Courier Service'),
            ('india_post', 'India Post'),
            ('blue_dart', 'Blue Dart'),
            ('dtdc', 'DTDC'),
            ('fedex', 'FedEx'),
            ('dhl', 'DHL'),
            ('delhivery', 'Delhivery'),
            ('ekart', 'Ekart'),
            (' other', 'Other'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    estimated_delivery_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        help_text='Optional: Expected delivery date'
    )
