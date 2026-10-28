from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from inventory.models import Category, Product, StockAuditLog
from khata.models import Customer, KhataTransaction
from assistant.models import ShopSettings, ShopFAQ


class Command(BaseCommand):
    help = 'Seeds initial sample data for Smart Dukaan (Categories, Products, Khata Customers, Shop Profile, and Admin)'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding sample data for Smart Dukaan...")

        # 1. Create Default Admin User
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@smartdukaan.local', 'admin123', first_name='Shopkeeper')
            self.stdout.write(self.style.SUCCESS("Created admin user: username='admin', password='admin123'"))

        # 2. Shop Settings
        shop, _ = ShopSettings.objects.get_or_create(id=1)
        shop.shop_name = "Apna Kirana & General Store"
        shop.tagline = "Smart Dukaan - Fresh Daily Essentials at Best Rates"
        shop.owner_name = "Rajesh Gupta"
        shop.phone = "+91 98765 43210"
        shop.address = "Shop #4, Gandhi Chowk, Main Bazaar, City"
        shop.opening_time = "8:00 AM"
        shop.closing_time = "10:00 PM"
        shop.weekly_off = "Open all 7 days"
        shop.upi_id = "apnakirana@okhdfcbank"
        shop.return_policy = "Returns accepted within 2 days with bill. Dairy and perishable goods cannot be returned."
        shop.custom_ai_instructions = "Always greet warmly with 'Namaste'. When a customer asks for a product, check price and stock availability accurately. Speak in English and Hinglish smoothly."
        shop.save()

        # 3. Sample FAQs
        faqs_data = [
            ("Do you provide home delivery?", "Yes! Free home delivery is available for orders above ₹300 within a 2 km radius. For smaller orders, a ₹20 delivery fee applies."),
            ("What payment methods do you accept?", "We accept Cash, UPI (Google Pay, PhonePe, Paytm), and Store Khata (for verified regular customers)."),
            ("Can I pay my pending Khata bill online?", "Yes! You can transfer via UPI to apnakirana@okhdfcbank and share the screenshot on WhatsApp to +91 98765 43210."),
            ("What are your shop timings on Sundays?", "We are open on all 7 days from 8:00 AM in the morning till 10:00 PM at night."),
        ]
        for q, a in faqs_data:
            ShopFAQ.objects.get_or_create(question=q, defaults={'answer': a})

        # 4. Categories
        cat_map = {}
        categories_data = [
            ("Groceries & Staples", "Flour, Rice, Pulses, Sugar, Salt, Spices, and Edible Oils"),
            ("Dairy & Bakery", "Milk, Curd, Butter, Paneer, and Fresh Bread"),
            ("Snacks & Instant Food", "Noodles, Biscuits, Chips, and Namkeen"),
            ("Beverages & Tea", "Tea leaves, Coffee, and Soft Drinks"),
            ("Personal & Home Care", "Soaps, Shampoos, Detergents, and Cleaning Supplies"),
        ]
        for name, desc in categories_data:
            cat, _ = Category.objects.get_or_create(name=name, defaults={'description': desc})
            cat_map[name] = cat

        # 5. Products
        products_data = [
            ("Aashirvaad Shudh Chakki Atta 5kg", "Groceries & Staples", "890103000001", 215.00, 245.00, 18, 5, "packet"),
            ("Tata Salt Vacuum Evaporated 1kg", "Groceries & Staples", "890103000002", 23.00, 28.00, 35, 10, "packet"),
            ("Fortune Sunlite Refined Sunflower Oil 1L", "Groceries & Staples", "890103000003", 125.00, 145.00, 12, 4, "packet"),
            ("Daawat Rozana Super Basmati Rice 1kg", "Groceries & Staples", "890103000004", 85.00, 110.00, 20, 5, "kg"),
            ("Madhur Pure & Hygienic Sugar 1kg", "Groceries & Staples", "890103000005", 38.00, 45.00, 4, 10, "kg"),  # Low stock item
            ("Amul Taaza Fresh Toned Milk 500ml", "Dairy & Bakery", "890103000006", 24.50, 27.00, 25, 6, "packet"),
            ("Amul Butter Pasteurised 100g", "Dairy & Bakery", "890103000007", 52.00, 58.00, 15, 5, "packet"),
            ("Maggi 2-Minute Masala Noodles 70g", "Snacks & Instant Food", "890103000008", 12.00, 14.00, 50, 12, "packet"),
            ("Parle-G Gold Glucose Biscuits 1kg", "Snacks & Instant Food", "890103000009", 90.00, 115.00, 8, 3, "packet"),
            ("Tata Tea Premium Desh Ki Chai 250g", "Beverages & Tea", "890103000010", 120.00, 145.00, 16, 5, "packet"),
            ("Dettol Original Germ Protection Soap 125g", "Personal & Home Care", "890103000011", 34.00, 42.00, 30, 8, "pcs"),
            ("Surf Excel Easy Wash Detergent Powder 1kg", "Personal & Home Care", "890103000012", 110.00, 135.00, 3, 5, "packet"), # Low stock item
        ]

        for name, cat_name, barcode, cost, selling, stock, threshold, unit in products_data:
            p, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    'category': cat_map.get(cat_name),
                    'barcode': barcode,
                    'cost_price': cost,
                    'selling_price': selling,
                    'stock_quantity': stock,
                    'low_stock_threshold': threshold,
                    'unit': unit,
                    'description': f"Quality {name} available at retail price."
                }
            )
            if created and stock > 0:
                StockAuditLog.objects.create(
                    product=p,
                    movement_type='RESTOCK',
                    quantity_changed=stock,
                    stock_after=stock,
                    reason="Initial Stock Setup"
                )

        # 6. Sample Khata Customers
        customers_data = [
            ("Ramesh Sharma", "+91 98765 11111", "House #12, Gali 3, Near Water Tank", 5000.00, 1450.00),
            ("Priya Verma", "+91 98765 22222", "Flat 204, Shanti Apartments", 3000.00, 620.00),
            ("Suresh Patel", "+91 98765 33333", "Shop #8, Market Square", 8000.00, 0.00),
        ]

        for name, phone, address, limit, balance in customers_data:
            cust, created = Customer.objects.get_or_create(
                phone=phone,
                defaults={
                    'name': name,
                    'address': address,
                    'credit_limit': limit,
                    'current_balance': balance
                }
            )
            if created and balance > 0:
                KhataTransaction.objects.create(
                    customer=cust,
                    transaction_type='CREDIT',
                    amount=balance,
                    payment_mode='OTHER',
                    balance_after=balance,
                    notes="Opening pending balance"
                )

        self.stdout.write(self.style.SUCCESS("Successfully seeded all sample data!"))
