from django.shortcuts import render, redirect, get_object_or_404
from .models import *

# 1. BROWSE: The home page (This was likely missing or misspelled)
def browse(request):
    products = Product.objects.all()
    return render(request, 'store/browse/list.html', {'products': products})

# 2. CUSTOMERS: View and Register Customers in-app
def customer_list(request):
    if request.method == "POST":
        Customer.objects.create(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            contact_number=request.POST.get('contact_number'),
            customer_address=request.POST.get('customer_address')
        )
        return redirect('customer_list')

    customers = Customer.objects.all()
    return render(request, 'store/customers/list.html', {'customers': customers})

# 3. STORES: View branch locations
def store_list(request):
    stores = Store.objects.all()
    return render(request, 'store/stores/list.html', {'stores': stores})

# 4. INVENTORY: Management
def inventory_manage(request):
    if request.method == "POST":
        store_obj = get_object_or_404(Store, id=request.POST.get('store_id'))
        product = Product.objects.create(
            product_name=request.POST.get('name'), 
            price=request.POST.get('price'), 
            store=store_obj
        )
        Inventory.objects.create(store=store_obj, product=product, quantity=request.POST.get('stock'))
        return redirect('inventory_manage')
        
    items = Inventory.objects.all()
    stores = Store.objects.all()
    return render(request, 'store/inventory/manage.html', {'items': items, 'stores': stores})

# 5. CHECKOUT & POS LOGIC
def add_to_checkout(request, product_id):
    customer = Customer.objects.first() 
    product = get_object_or_404(Product, id=product_id)
    order, _ = Order.objects.get_or_create(customer=customer, store=product.store, complete=False)
    OrderItem.objects.create(order=order, product=product, quantity=1)
    return redirect('browse')

def checkout_summary(request):
    customer = Customer.objects.first()
    order = Order.objects.filter(customer=customer, complete=False).first()
    items = order.orderitem_set.all() if order else []
    return render(request, 'store/checkout/summary.html', {'items': items, 'order': order})

def process_payment(request):
    customer = Customer.objects.first()
    order = get_object_or_404(Order, customer=customer, complete=False)
    for item in order.orderitem_set.all():
        inv = Inventory.objects.filter(product=item.product, store=order.store).first()
        if inv:
            inv.quantity -= item.quantity
            inv.save()
    order.complete = True
    order.save()
    return redirect('history_page')

def history_page(request):
    customer = Customer.objects.first()
    orders = Order.objects.filter(customer=customer, complete=True).order_by('-date_ordered')
    return render(request, 'store/history/list.html', {'orders': orders})