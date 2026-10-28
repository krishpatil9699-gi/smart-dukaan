from django.db import models

<<<<<<< HEAD

class ShopSettings(models.Model):
    shop_name = models.CharField(max_length=150, default="Smart Dukaan")
    tagline = models.CharField(max_length=255, default="Aapki Apni Digital Dukaan")
    owner_name = models.CharField(max_length=100, default="Shop Owner")
    phone = models.CharField(max_length=20, default="+91 98765 43210")
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(default="Main Market, Near Clock Tower, City Center")
    opening_time = models.CharField(max_length=50, default="8:00 AM")
    closing_time = models.CharField(max_length=50, default="10:00 PM")
    weekly_off = models.CharField(max_length=50, default="Open all 7 days")
    upi_id = models.CharField(max_length=100, blank=True, null=True, default="dukaan@upi")
    return_policy = models.TextField(default="Returns accepted within 2 days with valid invoice. Perishable goods non-returnable.")
    custom_ai_instructions = models.TextField(
        blank=True,
        null=True,
        help_text="Custom knowledge or personality guidelines for the Gemini AI assistant."
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Shop Setting"
        verbose_name_plural = "Shop Settings"

    def __str__(self):
        return self.shop_name


class ShopFAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.question
=======
# Create your models here.
>>>>>>> 1b21a4b3baae80a347efe13906d445db26a2bb0d
