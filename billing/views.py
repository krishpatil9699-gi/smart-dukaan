import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from inventory.models import Product, StockAuditLog
from khata.models import Customer, KhataTransaction
from assistant.models import ShopSettings
from .models import Order, OrderItem, generate_invoice_number


@login_required
def pos_view(request):
    """Interactive POS Terminal for quick barcode/search and instant cart billing."""
    products = Product.objects.filter(is_active=True).select_related('category')
    customers = Customer.objects.filter(is_active=True)
    shop = ShopSettings.objects.first()

    context = {
        'products': products,
        'customers': customers,
        'shop': shop,
    }
    return render(request, 'billing/pos.html', context)


@login_required
@csrf_exempt
def checkout_api(request):
    """Processes POS billing transaction with atomic stock decrement and Khata update."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=405)

    try:
        data = json.loads(request.body)
        items_data = data.get('items', [])
        payment_method = data.get('payment_method', 'CASH')
        customer_id = data.get('customer_id')
        discount_amount = float(data.get('discount_amount') or 0.0)
        notes = data.get('notes', '')

        if not items_data:
            return JsonResponse({'error': 'Cart is empty. Please add products.'}, status=400)

        customer = None
        if customer_id:
            customer = Customer.objects.filter(id=customer_id).first()

        if payment_method == 'CREDIT' and not customer:
            return JsonResponse({'error': 'A registered customer is required for Khata/Udhar billing.'}, status=400)

        with transaction.atomic():
            # 1. Calculate totals and check stock availability
            calculated_total = 0.0
            order_items_to_create = []

            for item in items_data:
                product_id = item.get('product_id')
                qty = int(item.get('quantity', 1))
                if qty <= 0:
                    continue

                product = Product.objects.select_for_update().get(id=product_id)
                if product.stock_quantity < qty:
                    return JsonResponse({
                        'error': f"Insufficient stock for '{product.name}'. Available: {product.stock_quantity} {product.unit}."
                    }, status=400)

                subtotal = float(product.selling_price) * qty
                calculated_total += subtotal

                # Deduct inventory stock
                product.stock_quantity -= qty
                product.save()

                # Audit log
                StockAuditLog.objects.create(
                    product=product,
                    movement_type='SALE',
                    quantity_changed=-qty,
                    stock_after=product.stock_quantity,
                    reason="POS Invoice Sale"
                )

                order_items_to_create.append({
                    'product': product,
                    'product_name': product.name,
                    'unit_price': product.selling_price,
                    'quantity': qty,
                    'subtotal': subtotal
                })

            net_payable = max(0.0, calculated_total - discount_amount)
            invoice_num = generate_invoice_number()

            # 2. Create the Order
            order = Order.objects.create(
                invoice_number=invoice_num,
                customer=customer,
                customer_name=customer.name if customer else data.get('customer_name', 'Walk-in Customer'),
                customer_phone=customer.phone if customer else data.get('customer_phone', ''),
                total_amount=calculated_total,
                discount_amount=discount_amount,
                net_payable=net_payable,
                payment_method=payment_method,
                status='COMPLETED',
                notes=notes
            )

            # 3. Create OrderItems
            for item_data in order_items_to_create:
                OrderItem.objects.create(
                    order=order,
                    product=item_data['product'],
                    product_name=item_data['product_name'],
                    unit_price=item_data['unit_price'],
                    quantity=item_data['quantity'],
                    subtotal=item_data['subtotal']
                )

            # 4. If Khata/Credit, update customer balance and ledger
            if payment_method == 'CREDIT' and customer:
                customer.current_balance = float(customer.current_balance) + net_payable
                customer.save()

                KhataTransaction.objects.create(
                    customer=customer,
                    transaction_type='CREDIT',
                    amount=net_payable,
                    payment_mode='OTHER',
                    balance_after=customer.current_balance,
                    notes=f"Auto-added from Invoice #{invoice_num}"
                )

        return JsonResponse({
            'success': True,
            'invoice_number': order.invoice_number,
            'order_id': order.id,
            'net_payable': float(order.net_payable)
        })

    except Product.DoesNotExist:
        return JsonResponse({'error': 'One of the selected products was not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def order_list_view(request):
    orders = Order.objects.all().select_related('customer')
    payment_filter = request.GET.get('payment_method')
    query = request.GET.get('q', '').strip()

    if payment_filter:
        orders = orders.filter(payment_method=payment_filter)
    if query:
        orders = orders.filter(invoice_number__icontains=query)

    return render(request, 'billing/order_list.html', {'orders': orders})


@login_required
def invoice_detail_view(request, invoice_number):
    order = get_object_or_404(Order, invoice_number=invoice_number)
    shop = ShopSettings.objects.first()
    return render(request, 'billing/invoice.html', {'order': order, 'shop': shop})
