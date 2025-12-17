# Generated migration to add delivery_charge field to OrderHistory

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0026_orderhistorystatus_orderstatuslog'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderhistory',
            name='delivery_charge',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Delivery charge for delivery orders', max_digits=10),
        ),
    ]
