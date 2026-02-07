from django.shortcuts import render, redirect, get_object_or_404
from .models import *

# 1. BROWSE: The home page (This was likely missing or misspelled)
def browse(request):
    products = Product.objects.all()
    customers = Customer.objects.all() # Get all customers for the POS dropdown
    return render(request, 'store/browse/list.html', {
        'products': products, 
        'customers': customers
    })
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
    if request.method == "POST":
        # Capture the data from the form
        name = request.POST.get('store_name')
        address = request.POST.get('store_address')
        
        # Create the store entry
        Store.objects.create(
            store_name=name,
            store_address=address
        )
        return redirect('store_list')

    stores = Store.objects.all()
    return render(request, 'store/stores/list.html', {'stores': stores})

# 4. INVENTORY: Management
def inventory_manage(request):
    if request.method == "POST":
        s_id = request.POST.get('store_id')
        name = request.POST.get('name')
        price = request.POST.get('price')
        # Changed this from 'stock' to 'quantity' to match your HTML
        qty_value = request.POST.get('quantity') 

        # Prevent IntegrityError by ensuring a value exists
        if not qty_value:
            qty_value = 0
        
        store_obj = get_object_or_404(Store, id=s_id)
        
        # 1. Create the Product
        product = Product.objects.create(
            product_name=name, 
            price=price, 
            store=store_obj
        )
        
        # 2. Create the Inventory entry
        Inventory.objects.create(
            store=store_obj, 
            product=product, 
            quantity=qty_value 
        )
        return redirect('inventory_manage')
        
    items = Inventory.objects.all()
    stores = Store.objects.all()
    return render(request, 'store/inventory/manage.html', {'items': items, 'stores': stores})

# 5. CHECKOUT & POS LOGIC
def add_to_checkout(request, product_id):
    # Get the customer ID from the URL or a form
    customer_id = request.GET.get('customer_id')
    
    if not customer_id:
        # Fallback to the first customer if none selected, 
        # but redirect to register if none exist in DB
        customer = Customer.objects.first()
        if not customer:
            return redirect('customer_list')
    else:
        customer = get_object_or_404(Customer, id=customer_id)

    product = get_object_or_404(Product, id=product_id)
    
    # This prevents the NOT NULL error by ensuring a valid customer object
    order, _ = Order.objects.get_or_create(
        customer=customer, 
        store=product.store, 
        complete=False
    )
    
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

