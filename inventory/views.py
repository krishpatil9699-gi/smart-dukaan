<<<<<<< HEAD
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category, StockAuditLog


@login_required
def product_list_view(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    filter_type = request.GET.get('filter', '')

    products = Product.objects.filter(is_active=True).select_related('category')

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(barcode__icontains=query) | Q(description__icontains=query)
        )

    if category_id:
        products = products.filter(category_id=category_id)

    if filter_type == 'low_stock':
        # Filter products where stock <= low_stock_threshold
        products = [p for p in products if p.is_low_stock]

    categories = Category.objects.all()
    
    # Calculate stats
    all_products = Product.objects.filter(is_active=True)
    total_products = all_products.count()
    low_stock_count = sum(1 for p in all_products if p.is_low_stock)
    out_of_stock_count = all_products.filter(stock_quantity__lte=0).count()

    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'filter_type': filter_type,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
    }
    return render(request, 'inventory/product_list.html', context)


@login_required
def product_create_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        barcode = request.POST.get('barcode') or None
        cost_price = request.POST.get('cost_price') or 0
        selling_price = request.POST.get('selling_price')
        stock_quantity = int(request.POST.get('stock_quantity') or 0)
        low_stock_threshold = int(request.POST.get('low_stock_threshold') or 5)
        unit = request.POST.get('unit') or 'pcs'
        description = request.POST.get('description', '')
        image = request.FILES.get('image')

        category = Category.objects.filter(id=category_id).first() if category_id else None

        product = Product.objects.create(
            name=name,
            category=category,
            barcode=barcode,
            cost_price=cost_price,
            selling_price=selling_price,
            stock_quantity=stock_quantity,
            low_stock_threshold=low_stock_threshold,
            unit=unit,
            description=description,
            image=image
        )

        # Log initial stock movement
        if stock_quantity > 0:
            StockAuditLog.objects.create(
                product=product,
                movement_type='RESTOCK',
                quantity_changed=stock_quantity,
                stock_after=stock_quantity,
                reason="Initial Stock on Product Creation"
            )

        messages.success(request, f"Product '{product.name}' added successfully!")
        return redirect('product_list')

    categories = Category.objects.all()
    return render(request, 'inventory/product_form.html', {'categories': categories, 'action': 'Add'})


@login_required
def product_edit_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product.name = request.POST.get('name', product.name)
        category_id = request.POST.get('category')
        product.category = Category.objects.filter(id=category_id).first() if category_id else None
        product.barcode = request.POST.get('barcode') or None
        product.cost_price = request.POST.get('cost_price', product.cost_price)
        product.selling_price = request.POST.get('selling_price', product.selling_price)
        product.low_stock_threshold = int(request.POST.get('low_stock_threshold', product.low_stock_threshold))
        product.unit = request.POST.get('unit', product.unit)
        product.description = request.POST.get('description', product.description)

        if 'image' in request.FILES:
            product.image = request.FILES['image']

        product.save()
        messages.success(request, f"Product '{product.name}' updated successfully!")
        return redirect('product_list')

    categories = Category.objects.all()
    return render(request, 'inventory/product_form.html', {'product': product, 'categories': categories, 'action': 'Edit'})


@login_required
def product_delete_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.is_active = False
    product.save()
    messages.success(request, f"Product '{product.name}' deactivated successfully.")
    return redirect('product_list')


@login_required
def quick_restock_view(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        qty_to_add = int(request.POST.get('quantity', 0))
        reason = request.POST.get('reason', 'Manual Restock')

        if qty_to_add != 0:
            product.stock_quantity += qty_to_add
            product.save()

            StockAuditLog.objects.create(
                product=product,
                movement_type='RESTOCK' if qty_to_add > 0 else 'ADJUSTMENT',
                quantity_changed=qty_to_add,
                stock_after=product.stock_quantity,
                reason=reason
            )
            messages.success(request, f"Stock updated for {product.name}. New balance: {product.stock_quantity} {product.unit}.")

    return redirect('product_list')


@login_required
def category_list_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        if name:
            Category.objects.get_or_create(name=name, defaults={'description': description})
            messages.success(request, f"Category '{name}' created!")
        return redirect('category_list')

    categories = Category.objects.all()
    return render(request, 'inventory/category_list.html', {'categories': categories})
=======
from django.shortcuts import render

# Create your views here.
>>>>>>> 1b21a4b3baae80a347efe13906d445db26a2bb0d
