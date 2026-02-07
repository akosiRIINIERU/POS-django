from django.urls import path
from . import views

urlpatterns = [
    path('', views.browse, name='browse'),
    path('inventory/', views.inventory_manage, name='inventory_manage'),
    path('customers/', views.customer_list, name='customer_list'),
    path('stores/', views.store_list, name='store_list'),
    path('buy/<int:product_id>/', views.add_to_checkout, name='add_to_checkout'),
    path('checkout/', views.checkout_summary, name='checkout_summary'),
    path('pay/', views.process_payment, name='process_payment'),
    path('history/', views.history_page, name='history_page'),
]