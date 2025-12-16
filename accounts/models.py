from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Staff(models.Model):
    STAFF_TYPE_CHOICES = [
        ('supervisor', 'Supervisor'),
        ('staff', 'Staff'),
        ('kitchen_staff', 'Kitchen Staff'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    staff_type = models.CharField(max_length=20, choices=STAFF_TYPE_CHOICES, default='staff')
    role = models.CharField(max_length=50)
    contact = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    joined_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_staff_type_display()})"

    def has_group(self, group_name):
        return self.user.groups.filter(name=group_name).exists()

    def has_permission(self, perm_codename):
        # Perm_codename may be either 'app_label.codename' or just codename
        if '.' in perm_codename:
            return self.user.has_perm(perm_codename)
        # try with app label 'restaurant' as default
        return self.user.has_perm(f"restaurant.{perm_codename}") or self.user.has_perm(perm_codename)
    
    def has_module_access(self, module_name):
        """Check if staff has access to a specific module"""
        return self.permissions.filter(module=module_name, is_allowed=True).exists()
    
    def get_allowed_modules(self):
        """Get list of all modules staff can access"""
        return self.permissions.filter(is_allowed=True).values_list('module', flat=True)
    
    def has_all_permissions(self):
        """Check if staff has access to ALL 8 modules"""
        total_modules = StaffPermission.MODULE_CHOICES.__len__()
        allowed_count = self.permissions.filter(is_allowed=True).count()
        return allowed_count == total_modules


class StaffPermission(models.Model):
    MODULE_CHOICES = [
        ('dashboard', 'Dashboard'),
        ('orders', 'Orders'),
        ('menu', 'Menu'),
        ('kitchen', 'Kitchen'),
        ('history', 'History'),
        ('tables', 'Tables'),
        ('takeaway', 'Take Away'),
        ('delivery', 'Delivery'),
    ]
    
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='permissions')
    module = models.CharField(max_length=50, choices=MODULE_CHOICES)
    is_allowed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('staff', 'module')
        verbose_name = 'Staff Permission'
        verbose_name_plural = 'Staff Permissions'
    
    def __str__(self):
        status = 'Allowed' if self.is_allowed else 'Denied'
        return f"{self.staff.user.username} - {self.get_module_display()} ({status})"