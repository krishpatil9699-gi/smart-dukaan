from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list_view, name='product_list'),
    path('add/', views.product_create_view, name='product_create'),
    path('<int:product_id>/edit/', views.product_edit_view, name='product_edit'),
    path('<int:product_id>/delete/', views.product_delete_view, name='product_delete'),
    path('<int:product_id>/restock/', views.quick_restock_view, name='quick_restock'),
    path('categories/', views.category_list_view, name='category_list'),
]
