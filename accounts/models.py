from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)
    contact = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    joined_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.role})"

    def has_group(self, group_name):
        return self.user.groups.filter(name=group_name).exists()

    def has_permission(self, perm_codename):
        # Perm_codename may be either 'app_label.codename' or just codename
        if '.' in perm_codename:
            return self.user.has_perm(perm_codename)
        # try with app label 'restaurant' as default
        return self.user.has_perm(f"restaurant.{perm_codename}") or self.user.has_perm(perm_codename)