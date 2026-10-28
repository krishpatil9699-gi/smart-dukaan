<<<<<<< HEAD
from datetime import timedelta
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from billing.models import Order, OrderItem
from inventory.models import Product
from khata.models import Customer


@login_required
def dashboard_view(request):
    """Main dashboard with KPI metric cards, Chart.js graphs, and alerts."""
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # 1. Financial KPIs
    today_orders = Order.objects.filter(created_at__gte=today_start, status='COMPLETED')
    today_sales = today_orders.aggregate(total=Sum('net_payable'))['total'] or 0.00
    today_orders_count = today_orders.count()

    month_orders = Order.objects.filter(created_at__gte=month_start, status='COMPLETED')
    month_sales = month_orders.aggregate(total=Sum('net_payable'))['total'] or 0.00

    # 2. Khata Pending Dues
    total_udhar = Customer.objects.filter(is_active=True).aggregate(total=Sum('current_balance'))['total'] or 0.00
    customers_due_count = Customer.objects.filter(is_active=True, current_balance__gt=0).count()

    # 3. Inventory Alerts
    all_products = Product.objects.filter(is_active=True)
    total_products = all_products.count()
    low_stock_products = [p for p in all_products if p.is_low_stock]
    low_stock_count = len(low_stock_products)

    # 4. Recent Invoices
    recent_orders = Order.objects.all().select_related('customer')[:7]

    context = {
        'today_sales': today_sales,
        'today_orders_count': today_orders_count,
        'month_sales': month_sales,
        'total_udhar': total_udhar,
        'customers_due_count': customers_due_count,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'low_stock_products': low_stock_products[:5],
        'recent_orders': recent_orders,
    }
    return render(request, 'dashboard/index.html', context)


@login_required
def sales_chart_api(request):
    """JSON API endpoint serving Chart.js graphs."""
    now = timezone.now()
    seven_days_ago = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)

    # 1. 7-Day Revenue Trend
    daily_sales = (
        Order.objects.filter(created_at__gte=seven_days_ago, status='COMPLETED')
        .annotate(sale_date=TruncDate('created_at'))
        .values('sale_date')
        .annotate(revenue=Sum('net_payable'), order_count=Count('id'))
        .order_by('sale_date')
    )

    date_map = {entry['sale_date'].strftime('%d %b'): float(entry['revenue'] or 0.0) for entry in daily_sales}
    
    # Generate continuous last 7 days labels
    labels = []
    revenue_data = []
    for i in range(7):
        day = (now - timedelta(days=6 - i)).date()
        day_str = day.strftime('%d %b')
        labels.append(day_str)
        revenue_data.append(date_map.get(day_str, 0.0))

    # 2. Payment Method Breakdown
    payment_breakdown = (
        Order.objects.filter(status='COMPLETED')
        .values('payment_method')
        .annotate(total=Sum('net_payable'))
    )
    payment_labels = [p['payment_method'] for p in payment_breakdown]
    payment_values = [float(p['total'] or 0.0) for p in payment_breakdown]

    # 3. Top 5 Products by Sales
    top_items = (
        OrderItem.objects.values('product_name')
        .annotate(total_qty=Sum('quantity'), total_sales=Sum('subtotal'))
        .order_by('-total_qty')[:5]
    )
    top_labels = [item['product_name'] for item in top_items]
    top_quantities = [item['total_qty'] for item in top_items]

    return JsonResponse({
        'revenue_trend': {
            'labels': labels,
            'data': revenue_data,
        },
        'payment_methods': {
            'labels': payment_labels if payment_labels else ['No Data'],
            'data': payment_values if payment_values else [0],
        },
        'top_products': {
            'labels': top_labels if top_labels else ['No Data'],
            'data': top_quantities if top_quantities else [0],
        }
    })
=======
from django.shortcuts import render

# Create your views here.
>>>>>>> 1b21a4b3baae80a347efe13906d445db26a2bb0d
