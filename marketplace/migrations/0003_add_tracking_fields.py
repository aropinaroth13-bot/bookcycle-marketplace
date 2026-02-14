# Generated manually for tracking fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0002_conversation_sellerrating_message_wishlist_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='tracking_number',
            field=models.CharField(blank=True, help_text='Courier tracking number', max_length=100),
        ),
        migrations.AddField(
            model_name='order',
            name='courier_service',
            field=models.CharField(
                blank=True,
                choices=[
                    ('india_post', 'India Post'),
                    ('blue_dart', 'Blue Dart'),
                    ('dtdc', 'DTDC'),
                    ('fedex', 'FedEx'),
                    ('dhl', 'DHL'),
                    ('delhivery', 'Delhivery'),
                    ('ekart', 'Ekart'),
                    ('other', 'Other'),
                ],
                help_text='Courier/Logistics service',
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='estimated_delivery_date',
            field=models.DateField(blank=True, help_text='Expected delivery date', null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='shipped_date',
            field=models.DateTimeField(blank=True, help_text='Date when order was shipped', null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='delivered_date',
            field=models.DateTimeField(blank=True, help_text='Date when order was delivered', null=True),
        ),
    ]
