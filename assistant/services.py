import os
import logging
from pathlib import Path
from dotenv import dotenv_values
from django.conf import settings
from .models import ShopSettings, ShopFAQ
from inventory.models import Product

logger = logging.getLogger(__name__)

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


def get_active_gemini_api_key():
    """Dynamically resolves API key from DB, Environment, or .env file."""
    # 1. Check database setting first (configured from dashboard UI)
    shop = ShopSettings.objects.first()
    if shop and shop.gemini_api_key:
        return shop.gemini_api_key.strip()

    # 2. Check process environment (e.g. Render/Railway environment variable)
    env_key = os.getenv("GEMINI_API_KEY", "").strip()
    if env_key:
        return env_key

    # 3. Check live .env file dynamically
    env_path = Path(settings.BASE_DIR) / '.env'
    if env_path.exists():
        vals = dotenv_values(env_path)
        file_key = (vals.get("GEMINI_API_KEY") or "").strip()
        if file_key:
            return file_key

    # 4. Check django settings
    return getattr(settings, 'GEMINI_API_KEY', '').strip()


def get_best_available_model(client):
    """Queries the Gemini API for currently active models supported by this specific API key."""
    fallback_priority = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-2.5-pro",
        "gemini-2.0-pro",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash-8b",
        "gemini-1.5-flash",
    ]

    try:
        # Dynamically list models available to this specific key on Google AI Studio
        model_pager = client.models.list()
        supported = [
            m.name.replace("models/", "")
            for m in model_pager
            if "generateContent" in (m.supported_actions or [])
        ]

        if supported:
            # Pick highest priority model that exists in available list
            for candidate in fallback_priority:
                if candidate in supported:
                    return candidate
            return supported[0]
    except Exception as e:
        logger.warning(f"Could not query models.list(): {e}")

    # Default to current generation flash
    return "gemini-2.5-flash"


def build_shop_context():
    """Compiles shop details, FAQs, and live inventory to ground Gemini responses."""
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

    # Fetch active FAQs
    faqs = ShopFAQ.objects.filter(is_active=True)
    faq_text = "\n".join([f"Q: {f.question}\nA: {f.answer}" for f in faqs])
    if not faq_text:
        faq_text = "No custom FAQs configured yet."

    # Fetch active products with current stock status
    products = Product.objects.filter(is_active=True).values('name', 'selling_price', 'stock_quantity', 'unit', 'category__name')
    catalog_lines = []
    for p in products:
        category = p['category__name'] or 'General'
        status = f"In Stock ({p['stock_quantity']} {p['unit']} available)" if p['stock_quantity'] > 0 else "Currently OUT OF STOCK"
        catalog_lines.append(f"- [{category}] {p['name']}: ₹{p['selling_price']} per {p['unit']} | {status}")
    
    catalog_text = "\n".join(catalog_lines) if catalog_lines else "No products listed in catalog currently."

    system_instruction = f"""
You are "Dukaan Sahayak" (दुकान सहायक), an intelligent, polite, and helpful AI assistant for "{shop.shop_name}".
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
2. If a customer asks for a product that is out of stock, politely inform them that it is currently out of stock.
3. If an item is not in the catalog at all, inform the user that the shop does not currently carry it.
4. Support English, Hindi, and Hinglish naturally depending on the customer's query.
5. Keep responses concise, clear, and friendly.
"""
    return system_instruction


def local_fallback_assistant(user_message: str) -> str:
    """Intelligent catalog parser that answers store queries cleanly without showing raw errors."""
    query = user_message.lower().strip()
    shop = ShopSettings.objects.first()

    shop_name = shop.shop_name if shop else "Smart Dukaan"
    timings = f"{shop.opening_time} to {shop.closing_time} ({shop.weekly_off})" if shop else "8:00 AM to 10:00 PM"
    address = shop.address if shop else "Market Center"
    phone = shop.phone if shop else "+91 98765 43210"
    upi = shop.upi_id if shop else "Not configured"
    returns = shop.return_policy if shop else "Returns within 2 days with invoice."

    # 1. Greetings
    if any(w in query for w in ["hi", "hello", "hey", "namaste", "pranam", "kese ho", "kaise ho"]):
        return f"Namaste! 🙏 Welcome to **{shop_name}**! How can I help you today? You can ask about product availability, prices, store timings, or policies."

    # 2. Timings / Hours
    if any(w in query for w in ["timing", "time", "hour", "open", "close", "kab khulta", "kab band"]):
        return f"🕒 **Store Timings for {shop_name}**:\nWe are open from **{timings}**."

    # 3. Address / Location
    if any(w in query for w in ["address", "location", "kaha hai", "where", "kahan"]):
        return f"📍 **Store Address**:\n{address}\nContact: {phone}"

    # 4. Payment / UPI
    if any(w in query for w in ["upi", "pay", "payment", "online", "gpay", "phonepe", "qr"]):
        return f"💳 **Payment Methods**:\nWe accept Cash, UPI, and Store Khata.\nOur UPI ID is: **{upi}**."

    # 5. Return / Refund
    if any(w in query for w in ["return", "refund", "exchange", "wapas"]):
        return f"🔄 **Return Policy**:\n{returns}"

    # 6. Delivery
    if any(w in query for w in ["delivery", "home delivery", "ghar"]):
        delivery_faq = ShopFAQ.objects.filter(question__icontains="delivery").first()
        if delivery_faq:
            return f"🚚 **Delivery Info**:\n{delivery_faq.answer}"
        return f"🚚 Home delivery is available for nearby orders! Please call us directly at **{phone}** to place a delivery order."

    # 7. Product Search in Live Inventory
    all_products = Product.objects.filter(is_active=True)
    matched_products = []
    stopwords = {"what", "is", "the", "price", "of", "do", "you", "have", "in", "stock", "available", "cost", "rate", "and", "please", "kya", "hai", "bhav"}
    keywords = [k for k in query.replace("?", "").replace(",", "").split() if k not in stopwords and len(k) > 2]

    for p in all_products:
        p_name_lower = p.name.lower()
        if any(k in p_name_lower for k in keywords) or (keywords and any(p_word in keywords for p_word in p_name_lower.split())):
            matched_products.append(p)

    if matched_products:
        res = "🛒 **Live Product Search Results**:\n"
        for p in matched_products[:4]:
            if p.stock_quantity > 0:
                res += f"• **{p.name}**: ₹{p.selling_price:.2f} per {p.unit} — *In Stock ({p.stock_quantity} {p.unit} left)*\n"
            else:
                res += f"• **{p.name}**: ₹{p.selling_price:.2f} per {p.unit} — ⚠️ *Currently Out of Stock*\n"
        return res.strip()

    # 8. Check Custom FAQs
    for faq in ShopFAQ.objects.filter(is_active=True):
        faq_words = [w for w in faq.question.lower().replace("?", "").split() if len(w) > 3 and w not in stopwords]
        if sum(1 for w in faq_words if w in query) >= 2:
            return f"💡 **{faq.question}**\n{faq.answer}"

    return (
        f"I couldn't find an exact match in our store catalog for '{user_message}'. "
        f"Please feel free to call our shop directly at **{phone}** for assistance!"
    )


def ask_shop_assistant(user_message: str) -> str:
    """Invokes Google Gemini with dynamic model discovery and clean fallback."""
    api_key = get_active_gemini_api_key()

    if not api_key or not GENAI_AVAILABLE:
        return local_fallback_assistant(user_message)

    try:
        client = genai.Client(api_key=api_key)
        system_instruction = build_shop_context()

        # Find the best active model supported by this key
        target_model = get_best_available_model(client)

        # Attempt generation
        response = client.models.generate_content(
            model=target_model,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3,
                max_output_tokens=350,
            )
        )
        if response and response.text:
            return response.text

    except Exception as e:
        logger.error(f"Gemini API invocation error: {e}")

    # Seamless fallback answering without raw stack traces
    return local_fallback_assistant(user_message)
