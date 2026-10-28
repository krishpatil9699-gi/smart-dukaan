from django.contrib import admin
from .models import ShopSettings, ShopFAQ


@admin.register(ShopSettings)
class ShopSettingsAdmin(admin.ModelAdmin):
    list_display = ('shop_name', 'owner_name', 'phone', 'opening_time', 'closing_time', 'updated_at')


@admin.register(ShopFAQ)
class ShopFAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('question', 'answer')
