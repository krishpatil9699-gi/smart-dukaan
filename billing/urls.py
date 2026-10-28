from django.urls import path
from . import views

urlpatterns = [
    path('pos/', views.pos_view, name='pos'),
    path('api/checkout/', views.checkout_api, name='checkout_api'),
    path('orders/', views.order_list_view, name='order_list'),
    path('invoice/<str:invoice_number>/', views.invoice_detail_view, name='invoice_detail'),
]
