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