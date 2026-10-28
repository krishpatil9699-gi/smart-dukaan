import os
from django.conf import settings
from .models import ShopSettings, ShopFAQ
from inventory.models import Product

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY") or getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


def build_shop_context():
    """Compiles shop details, FAQs, and live inventory to ground Gemini responses."""
    # 1. Fetch shop profile
    shop = ShopSettings.objects.first()
    if not shop:
        shop = ShopSettings.objects.create(
            shop_name="Smart Dukaan",
            tagline="Aapki Apni Digital Dukaan",
            owner_name="Shop Owner",
            phone="+91 98765 43210",
            address="Main Market, City Center",
            opening_time="8:00 AM",
            closing_time="10:00 PM",
            weekly_off="Open all 7 days",
            return_policy="Returns accepted within 2 days with valid invoice.",
        )

    # 2. Fetch active FAQs
    faqs = ShopFAQ.objects.filter(is_active=True)
    faq_text = "\n".join([f"Q: {f.question}\nA: {f.answer}" for f in faqs])
    if not faq_text:
        faq_text = "No custom FAQs configured yet."

    # 3. Fetch active products with current stock status
    products = Product.objects.filter(is_active=True).values('name', 'selling_price', 'stock_quantity', 'unit', 'category__name')
    catalog_lines = []
    for p in products:
        category = p['category__name'] or 'General'
        status = f"In Stock ({p['stock_quantity']} {p['unit']} available)" if p['stock_quantity'] > 0 else "Currently OUT OF STOCK"
        catalog_lines.append(f"- [{category}] {p['name']}: ₹{p['selling_price']} per {p['unit']} | {status}")
    
    catalog_text = "\n".join(catalog_lines) if catalog_lines else "No products listed in catalog currently."

    system_instruction = f"""
You are "Dukaan Sahayak" (दुकान सहायक), an intelligent, polite, and helpful AI virtual assistant for "{shop.shop_name}".
Tagline: {shop.tagline}

Shop Information:
- Owner: {shop.owner_name}
- Contact / Phone: {shop.phone}
- Store Address: {shop.address}
- Working Hours: {shop.opening_time} to {shop.closing_time} ({shop.weekly_off})
- Payment Methods Accepted: Cash, UPI (QR / PhonePe / GPay / Paytm), and Store Credit (Khata for registered customers)
- UPI ID: {shop.upi_id}
- Return & Exchange Policy: {shop.return_policy}

Frequently Asked Questions (Shop Rules & Policies):
{faq_text}

Real-Time Live Product Catalog & Inventory:
{catalog_text}

Additional Shop Owner Instructions:
{shop.custom_ai_instructions or "Be warm, helpful, and concise. You can converse comfortably in English and Hindi/Hinglish."}

Your Guidelines:
1. Always base product availability and prices strictly on the live catalog above.
2. If a customer asks for a product that is out of stock, politely inform them that it is currently out of stock and offer to check back soon.
3. If an item is not in the catalog at all, inform the user that the shop does not currently carry it.
4. Support both English, Hindi, and Hinglish naturally depending on the customer's query.
5. Keep responses short, clear, and retail-friendly (ideal for chat bubbles).
"""
    return system_instruction


def ask_shop_assistant(user_message: str) -> str:
    """Invokes Google Gemini with system instructions and dynamic grounding context."""
    if not GENAI_AVAILABLE:
        return "Gemini SDK (`google-genai`) is not installed. Please check requirements."

    api_key = os.getenv("GEMINI_API_KEY") or getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key:
        return (
            "⚠️ Gemini API Key is not configured yet! "
            "Please add your `GEMINI_API_KEY=your_key` in the `.env` file to enable live AI responses. "
            "(Meanwhile, you can still browse the digital catalogue and shop inventory)."
        )

    try:
        client = get_gemini_client()
        system_instruction = build_shop_context()

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3,
                max_output_tokens=350,
            )
        )
        return response.text
    except Exception as e:
        return f"Dukaan Sahayak is momentarily unavailable: {str(e)}"
