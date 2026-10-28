from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('api/sales-chart/', views.sales_chart_api, name='sales_chart_api'),
]
