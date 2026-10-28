from django.contrib import admin
from .models import Customer, KhataTransaction


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'current_balance', 'credit_limit', 'available_credit', 'is_active', 'created_at')
    search_fields = ('name', 'phone')
    list_filter = ('is_active',)


@admin.register(KhataTransaction)
class KhataTransactionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'transaction_type', 'amount', 'payment_mode', 'balance_after', 'date')
    list_filter = ('transaction_type', 'payment_mode', 'date')
    search_fields = ('customer__name', 'customer__phone', 'notes')
