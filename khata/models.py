from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=5000.00)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Positive = Pending Udhar
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    @property
    def available_credit(self):
        return max(0, float(self.credit_limit) - float(self.current_balance))

    def __str__(self):
        return f"{self.name} ({self.phone}) - Udhar: ₹{self.current_balance}"


class KhataTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('CREDIT', 'Udhar Given (Credit)'),
        ('PAYMENT', 'Payment Received (Debit/Jama)'),
    )

    PAYMENT_MODES = (
        ('CASH', 'Cash'),
        ('UPI', 'UPI / QR'),
        ('BANK', 'Bank Transfer'),
        ('OTHER', 'Other'),
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=10, choices=PAYMENT_MODES, default='CASH')
    balance_after = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notes = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.customer.name} | {self.transaction_type} | ₹{self.amount} on {self.date.strftime('%Y-%m-%d')}"
