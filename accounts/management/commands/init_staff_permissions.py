"""
Management command to initialize staff permissions
Run: python manage.py init_staff_permissions
"""

from django.core.management.base import BaseCommand
from accounts.models import Staff, StaffPermission


class Command(BaseCommand):
    help = 'Initialize staff permissions for all staff members'

    def handle(self, *args, **options):
        # Get all modules
        modules = [
            'dashboard',
            'orders',
            'menu',
            'kitchen',
            'history',
            'tables',
            'takeaway',
            'delivery',
        ]

        # For each staff member
        for staff in Staff.objects.all():
            # Create permission entries for each module if they don't exist
            for module in modules:
                permission, created = StaffPermission.objects.get_or_create(
                    staff=staff,
                    module=module,
                    defaults={'is_allowed': False}
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Created permission: {staff.user.username} - {module}'
                        )
                    )

        # Summary
        total_staff = Staff.objects.count()
        total_permissions = StaffPermission.objects.count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Initialization complete!'
                f'\n  Staff members: {total_staff}'
                f'\n  Total permissions: {total_permissions}'
            )
        )
