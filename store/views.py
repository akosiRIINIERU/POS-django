from django.shortcuts import render, redirect, get_object_or_404
from .models import *

# 1. BROWSE: Home page (FIXED INDENTATION HERE)
def browse(request):
    # This filters for stock > 0. If you haven't added stock yet, this page will be empty!
    products = Product.objects.filter(inventory__quantity__gt=0)
    customers = Customer.objects.all()
    selected_customer_id = request.GET.get('customer_id')
    return render(request, 'store/browse/list.html', {
        'products': products, 
        'customers': customers,
        'selected_customer_id': selected_customer_id
    })

def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('browse')

def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    customer.delete()
    return redirect('customer_list')

# 2. CUSTOMERS: Register in-app
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

# 3. STORES: Manage branch locations
def store_list(request):
    if request.method == "POST":
        Store.objects.create(
            store_name=request.POST.get('store_name'),
            store_address=request.POST.get('store_address')
        )
        return redirect('store_list')

    stores = Store.objects.all()
    return render(request, 'store/stores/list.html', {'stores': stores})

# 4. INVENTORY: Stock management (Prevents NOT NULL errors)
def inventory_manage(request):
    if request.method == "POST":
        s_id = request.POST.get('store_id')
        qty_value = request.POST.get('quantity') or 0 # Prevents IntegrityError
        
        store_obj = get_object_or_404(Store, id=s_id)
        product = Product.objects.create(
            product_name=request.POST.get('name'), 
            price=request.POST.get('price'), 
            store=store_obj
        )
        Inventory.objects.create(store=store_obj, product=product, quantity=qty_value)
        return redirect('inventory_manage')
        
    items = Inventory.objects.all()
    stores = Store.objects.all()
    return render(request, 'store/inventory/manage.html', {'items': items, 'stores': stores})

# 5. POS LOGIC: Dynamic Customer Cart
def add_to_checkout(request, product_id):
    # This line is the secret: it grabs the ID from your dropdown select
    customer_id = request.GET.get('customer_id')
    
    # Safety: If no ID, redirect to register to avoid the IntegrityError
    if not customer_id:
        return redirect('customer_list')

    customer = get_object_or_404(Customer, id=customer_id)
    product = get_object_or_404(Product, id=product_id)
    
    # This ensures the Order is linked to C2 specifically
    order, _ = Order.objects.get_or_create(customer=customer, store=product.store, complete=False)
    OrderItem.objects.create(order=order, product=product, quantity=1)
    
    # Stay on browse but keep C2 selected in the URL
    return redirect(f'/?customer_id={customer.id}')

def checkout_summary(request):
    # Get ID from URL, e.g., /checkout/?customer_id=3
    customer_id = request.GET.get('customer_id')
    
    # Fetch all customers so we can show them in a dropdown
    all_customers = Customer.objects.all() 
    
    # Get the specific customer or default to the first one (Erika)
    customer = Customer.objects.filter(id=customer_id).first() or Customer.objects.first()
    
    # Get the active order for the selected person
    order = Order.objects.filter(customer=customer, complete=False).first()
    items = order.orderitem_set.all() if order else []
    
    return render(request, 'store/checkout/summary.html', {
        'items': items, 
        'order': order, 
        'customer': customer,
        'all_customers': all_customers # Now you can see everyone in the cart!
    })

def process_payment(request):
    # Get ID from hidden input in the form
    customer_id = request.POST.get('customer_id')
    customer = get_object_or_404(Customer, id=customer_id)
    
    order = get_object_or_404(Order, customer=customer, complete=False)
    
    # Deduct stock as you requested
    for item in order.orderitem_set.all():
        inv = Inventory.objects.filter(product=item.product, store=order.store).first()
        if inv:
            inv.quantity -= item.quantity
            inv.save()
            
    order.complete = True
    order.save()
    
    # Redirect to history for THIS specific customer
    return redirect(f'/history/?customer_id={customer.id}')

def history_page(request):
    # Get the ID from the URL (e.g., /history/?customer_id=3)
    customer_id = request.GET.get('customer_id')
    
    # Fetch all customers so we can switch between them in the UI
    all_customers = Customer.objects.all()
    
    # Find the specific customer or fallback to the first one
    customer = Customer.objects.filter(id=customer_id).first() or Customer.objects.first()
    
    # Filter only for COMPLETED orders (complete=True) for this specific person
    orders = Order.objects.filter(customer=customer, complete=True).order_by('-date_ordered')
    
    return render(request, 'store/history/list.html', {
        'orders': orders, 
        'customer': customer,
        'all_customers': all_customers
    })