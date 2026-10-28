from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    UNIT_CHOICES = (
        ('pcs', 'Pieces (pcs)'),
        ('kg', 'Kilogram (kg)'),
        ('gm', 'Gram (gm)'),
        ('litre', 'Litre (L)'),
        ('ml', 'Millilitre (ml)'),
        ('packet', 'Packet (pkt)'),
        ('box', 'Box'),
        ('meter', 'Meter (m)'),
    )

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    name = models.CharField(max_length=200)
    barcode = models.CharField(max_length=60, blank=True, null=True, unique=True)
    description = models.TextField(blank=True, null=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=5)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='pcs')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold

    @property
    def margin(self):
        return self.selling_price - self.cost_price

    def __str__(self):
        return f"{self.name} - ₹{self.selling_price} ({self.stock_quantity} {self.unit})"


class StockAuditLog(models.Model):
    MOVEMENT_TYPES = (
        ('RESTOCK', 'Stock Added / Purchase'),
        ('SALE', 'Sold via POS Billing'),
        ('ADJUSTMENT', 'Manual Adjustment / Damage'),
        ('RETURN', 'Customer Return'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_logs')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity_changed = models.IntegerField()
    stock_after = models.IntegerField()
    reason = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} | {self.movement_type} | {self.quantity_changed} | Balance: {self.stock_after}"
