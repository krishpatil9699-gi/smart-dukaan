from django.contrib import admin
<<<<<<< HEAD
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'created_at')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'phone')
=======

# Register your models here.
>>>>>>> 1b21a4b3baae80a347efe13906d445db26a2bb0d
