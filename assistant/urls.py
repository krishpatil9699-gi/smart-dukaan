from django.urls import path
from . import views

urlpatterns = [
    path('api/chat/', views.chat_api, name='assistant_chat_api'),
    path('settings/', views.shop_settings_view, name='shop_settings'),
    path('faq/add/', views.add_faq_view, name='add_faq'),
    path('faq/<int:faq_id>/delete/', views.delete_faq_view, name='delete_faq'),
]
