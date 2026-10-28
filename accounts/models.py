from django.db import models
<<<<<<< HEAD
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('OWNER', 'Store Owner / Admin'),
        ('MANAGER', 'Store Manager'),
        ('CASHIER', 'Billing Cashier'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='OWNER')
    phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
=======

# Create your models here.
>>>>>>> 1b21a4b3baae80a347efe13906d445db26a2bb0d
