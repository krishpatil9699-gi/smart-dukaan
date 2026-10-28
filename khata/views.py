import urllib.parse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Q
from .models import Customer, KhataTransaction
from assistant.models import ShopSettings


@login_required
def customer_list_view(request):
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')

    customers = Customer.objects.filter(is_active=True)

    if query:
        customers = customers.filter(
            Q(name__icontains=query) | Q(phone__icontains=query)
        )

    if status_filter == 'due_only':
        customers = customers.filter(current_balance__gt=0)

    # Summary metrics
    total_udhar = Customer.objects.filter(is_active=True).aggregate(total=Sum('current_balance'))['total'] or 0.00
    customers_with_dues = Customer.objects.filter(is_active=True, current_balance__gt=0).count()
    total_customers = Customer.objects.filter(is_active=True).count()

    context = {
        'customers': customers,
        'query': query,
        'status_filter': status_filter,
        'total_udhar': total_udhar,
        'customers_with_dues': customers_with_dues,
        'total_customers': total_customers,
    }
    return render(request, 'khata/customer_list.html', context)


@login_required
def customer_detail_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    transactions = customer.transactions.all()
    shop = ShopSettings.objects.first()

    # Pre-generate WhatsApp message
    shop_name = shop.shop_name if shop else "Smart Dukaan"
    upi_id = shop.upi_id if shop else ""
    reminder_text = (
        f"Namaste {customer.name},\n"
        f"This is a gentle reminder from *{shop_name}* regarding your pending Khata balance of *₹{customer.current_balance}*.\n"
    )
    if upi_id:
        reminder_text += f"You can clear this via UPI to: *{upi_id}*.\n"
    reminder_text += "Thank you for shopping with us!"

    wa_phone = customer.phone.replace("+", "").replace(" ", "").replace("-", "")
    if len(wa_phone) == 10:
        wa_phone = "91" + wa_phone

    wa_link = f"https://wa.me/{wa_phone}?text={urllib.parse.quote(reminder_text)}"

    context = {
        'customer': customer,
        'transactions': transactions,
        'wa_link': wa_link,
        'shop': shop,
    }
    return render(request, 'khata/customer_detail.html', context)


@login_required
def customer_create_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        credit_limit = float(request.POST.get('credit_limit') or 5000.00)

        if Customer.objects.filter(phone=phone).exists():
            messages.error(request, f"Customer with phone {phone} already exists!")
            return redirect('customer_list')

        customer = Customer.objects.create(
            name=name,
            phone=phone,
            address=address,
            credit_limit=credit_limit,
            current_balance=0.00
        )
        messages.success(request, f"Customer '{customer.name}' added to Khata book!")
        return redirect('customer_detail', customer_id=customer.id)

    return redirect('customer_list')


@login_required
def add_transaction_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    if request.method == 'POST':
        tx_type = request.POST.get('transaction_type')  # 'CREDIT' or 'PAYMENT'
        amount = float(request.POST.get('amount') or 0.0)
        payment_mode = request.POST.get('payment_mode', 'CASH')
        notes = request.POST.get('notes', '').strip()

        if amount <= 0:
            messages.error(request, "Transaction amount must be greater than zero.")
            return redirect('customer_detail', customer_id=customer.id)

        with transaction.atomic():
            if tx_type == 'CREDIT':
                # Adding Udhar
                customer.current_balance = float(customer.current_balance) + amount
            else:
                # Customer Paid (Jama)
                customer.current_balance = max(0.0, float(customer.current_balance) - amount)

            customer.save()

            KhataTransaction.objects.create(
                customer=customer,
                transaction_type=tx_type,
                amount=amount,
                payment_mode=payment_mode,
                balance_after=customer.current_balance,
                notes=notes
            )

        messages.success(request, f"Transaction recorded! Updated balance: ₹{customer.current_balance}")
        return redirect('customer_detail', customer_id=customer.id)

    return redirect('customer_detail', customer_id=customer.id)
