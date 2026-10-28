from django.shortcuts import render
from inventory.models import Product, Category
from assistant.models import ShopSettings, ShopFAQ


def storefront_view(request):
    """Customer-facing digital catalogue & AI FAQ assistant."""
    shop = ShopSettings.objects.first()
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True).select_related('category')

    selected_category = request.GET.get('category')
    query = request.GET.get('q', '').strip()

    if selected_category:
        products = products.filter(category_id=selected_category)
    if query:
        products = products.filter(name__icontains=query)

    context = {
        'shop': shop,
        'categories': categories,
        'products': products,
        'selected_category': selected_category,
        'query': query,
    }
    return render(request, 'storefront/index.html', context)
