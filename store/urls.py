from django.urls import path
from . import views

urlpatterns = [
    path('', views.browse, name='browse'),
    path('inventory/', views.inventory_manage, name='inventory_manage'),
    path('customers/', views.customer_list, name='customer_list'),
    path('stores/', views.store_list, name='store_list'),
    # --- ADD THIS LINE TO FIX THE NoReverseMatch ERROR ---
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    # -----------------------------------------------------
    path('buy/<int:product_id>/', views.add_to_checkout, name='add_to_checkout'),
    path('checkout/', views.checkout_summary, name='checkout_summary'),
    path('pay/', views.process_payment, name='process_payment'),
    path('history/', views.history_page, name='history_page'),
    path('delete-customer/<int:customer_id>/', views.delete_customer, name='delete_customer'),
]