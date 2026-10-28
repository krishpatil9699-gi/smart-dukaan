from django.test import TestCase, Client
from django.urls import reverse
from inventory.models import Category, Product
from khata.models import Customer
from billing.models import Order, OrderItem
from assistant.services import build_shop_context
import json


class SmartDukaanTests(TestCase):
    def setUp(self):
        self.client = Client()
        from django.contrib.auth.models import User
        self.user = User.objects.create_user(username='cashier', password='password123')
        self.client.login(username='cashier', password='password123')

        # Category & Product
        self.category = Category.objects.create(name="Groceries")
        self.product = Product.objects.create(
            category=self.category,
            name="Sugar 1kg",
            cost_price=35.00,
            selling_price=42.00,
            stock_quantity=10,
            low_stock_threshold=5,
            unit="kg"
        )

        # Customer
        self.customer = Customer.objects.create(
            name="Amit Kumar",
            phone="9999988888",
            credit_limit=2000.00,
            current_balance=0.00
        )

    def test_low_stock_property(self):
        self.assertFalse(self.product.is_low_stock)
        self.product.stock_quantity = 3
        self.product.save()
        self.assertTrue(self.product.is_low_stock)

    def test_checkout_cash_sale(self):
        payload = {
            "items": [{"product_id": self.product.id, "quantity": 2}],
            "payment_method": "CASH",
            "discount_amount": 4.00,
        }
        response = self.client.post(
            reverse('checkout_api'),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['net_payable'], 80.00)  # (42 * 2) - 4 = 80

        # Stock should be decremented from 10 to 8
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 8)

    def test_checkout_khata_credit_sale(self):
        payload = {
            "items": [{"product_id": self.product.id, "quantity": 1}],
            "payment_method": "CREDIT",
            "customer_id": self.customer.id,
            "discount_amount": 0.00,
        }
        response = self.client.post(
            reverse('checkout_api'),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.customer.refresh_from_db()
        self.assertEqual(float(self.customer.current_balance), 42.00)

    def test_assistant_context_generation(self):
        context = build_shop_context()
        self.assertIn("Dukaan Sahayak", context)
        self.assertIn("Sugar 1kg", context)
