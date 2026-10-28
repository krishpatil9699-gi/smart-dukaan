import uuid
from django.db import models
from inventory.models import Product
from khata.models import Customer


def generate_invoice_number():
    import random
    import time
    return f"INV-{int(time.time())}-{random.randint(100, 999)}"


class Order(models.Model):
    PAYMENT_CHOICES = (
        ('CASH', 'Cash'),
        ('UPI', 'UPI / QR'),
        ('CREDIT', 'Udhar (Khata)'),
    )

    STATUS_CHOICES = (
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )

    invoice_number = models.CharField(max_length=64, unique=True, default=generate_invoice_number)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    customer_name = models.CharField(max_length=150, blank=True, null=True)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_payable = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='CASH')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='COMPLETED')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.invoice_number} - ₹{self.net_payable} ({self.payment_method})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    product_name = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x {self.quantity} = ₹{self.subtotal}"
