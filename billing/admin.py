from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'unit_price', 'quantity', 'subtotal')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'customer_name', 'payment_method', 'total_amount', 'discount_amount', 'net_payable', 'status', 'created_at')
    list_filter = ('payment_method', 'status', 'created_at')
    search_fields = ('invoice_number', 'customer_name', 'customer_phone')
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'unit_price', 'quantity', 'subtotal')
    search_fields = ('product_name', 'order__invoice_number')
