# Generated migration for Staff model updates

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        # Add staff_type field to Staff model
        migrations.AddField(
            model_name='staff',
            name='staff_type',
            field=models.CharField(
                choices=[('supervisor', 'Supervisor'), ('staff', 'Staff'), ('kitchen_staff', 'Kitchen Staff')],
                default='staff',
                max_length=20
            ),
        ),
        
        # Alter related_name for User foreign key
        migrations.AlterField(
            model_name='staff',
            name='user',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='staff_profile',
                to='accounts.user'
            ),
        ),
        
        # Create StaffPermission model
        migrations.CreateModel(
            name='StaffPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module', models.CharField(
                    choices=[
                        ('dashboard', 'Dashboard'),
                        ('orders', 'Orders'),
                        ('menu', 'Menu'),
                        ('kitchen', 'Kitchen'),
                        ('history', 'History'),
                        ('tables', 'Tables'),
                        ('takeaway', 'Take Away'),
                        ('delivery', 'Delivery'),
                    ],
                    max_length=50
                )),
                ('is_allowed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='permissions', to='accounts.staff')),
            ],
            options={
                'verbose_name': 'Staff Permission',
                'verbose_name_plural': 'Staff Permissions',
            },
        ),
        
        # Add unique constraint
        migrations.AddConstraint(
            model_name='staffpermission',
            constraint=models.UniqueConstraint(
                fields=('staff', 'module'),
                name='unique_staff_module'
            ),
        ),
    ]
