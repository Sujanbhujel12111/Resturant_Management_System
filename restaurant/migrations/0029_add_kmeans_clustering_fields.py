# Generated migration for K-Means clustering fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0028_alter_orderhistory_payment_method_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='demand_tier',
            field=models.CharField(
                choices=[
                    ('high', 'High Demand (Tier 1)'),
                    ('medium', 'Medium Demand (Tier 2)'),
                    ('low', 'Low Demand (Tier 3)')
                ],
                default='medium',
                help_text='Demand tier calculated by K-Means clustering on order history',
                max_length=10
            ),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='order_count',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Total number of times this item was ordered'
            ),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='last_tier_update',
            field=models.DateTimeField(
                null=True,
                blank=True,
                help_text='Last time the demand tier was recalculated'
            ),
        ),
    ]
