from django.urls import path
from . import views

urlpatterns = [
    path('', views.customer_list_view, name='customer_list'),
    path('add/', views.customer_create_view, name='customer_create'),
    path('<int:customer_id>/', views.customer_detail_view, name='customer_detail'),
    path('<int:customer_id>/transaction/', views.add_transaction_view, name='add_transaction'),
]
