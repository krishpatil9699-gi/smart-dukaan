from django.contrib import admin
<<<<<<< HEAD
from .models import Category, Product, StockAuditLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'selling_price', 'cost_price', 'stock_quantity', 'unit', 'is_low_stock', 'is_active')
    list_filter = ('category', 'is_active', 'unit')
    search_fields = ('name', 'barcode')
    list_editable = ('selling_price', 'stock_quantity', 'is_active')


@admin.register(StockAuditLog)
class StockAuditLogAdmin(admin.ModelAdmin):
    list_display = ('product', 'movement_type', 'quantity_changed', 'stock_after', 'reason', 'timestamp')
    list_filter = ('movement_type', 'timestamp')
    search_fields = ('product__name', 'reason')
=======

# Register your models here.
>>>>>>> 1b21a4b3baae80a347efe13906d445db26a2bb0d
