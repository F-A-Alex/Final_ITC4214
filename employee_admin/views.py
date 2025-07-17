from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.template import TemplateDoesNotExist
from django.db.models import Q
import os
from store.models import Product, Category, Subcategory, Order
from .forms import ProductForm, OrderForm
from functools import wraps

#Check if staff and generate custom error message
def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render_403(request, "You must be logged in to access this page.")
        if not request.user.is_staff:
            return render_403(request, "You must be a staff member to access this page.")
        return view_func(request, *args, **kwargs)
    return wrapper

#Check render the custom 403 page with specific error message
def render_403(request, message="Access Denied"):
    try:
        return render(request, 'errors/403.html', {
            'error_message': message
        }, status=403)
    except TemplateDoesNotExist:
        return HttpResponseForbidden(message)


#Admin dashboard
@staff_required
def admin_dashboard(request):
    try:
        #Get statistics on active products - stock level 
        total_products = Product.objects.count()
        active_products = Product.objects.filter(is_active=True).count()
        low_stock_products = Product.objects.filter(
            stock_quantity__lt=5, 
            is_active=True
        ).select_related('category', 'subcategory')
        
        #Get statistics on orders and status
        total_orders = Order.objects.count()
        active_orders = Order.objects.exclude(status__in=['delivered', 'cancelled']).count()
        recent_orders = Order.objects.select_related('user').all()[:5]
        
        return render(request, 'employee_admin/dashboard.html', {
            'total_products': total_products,
            'active_products': active_products,
            'total_orders': total_orders,
            'active_orders': active_orders,
            'recent_orders': recent_orders,
            'low_stock_products': low_stock_products,
        })
    #fallbck if error
    except Exception:
        return render(request, 'employee_admin/dashboard.html', {
            'total_products': 0,
            'active_products': 0,
            'total_orders': 0,
           'active_orders': 0,
            'recent_orders': [],
            'low_stock_products': [],
        })


#Admin Products Database Page
@staff_required
def admin_products(request):
    try:
        products = Product.objects.select_related('category', 'subcategory', 'created_by').order_by('-created_at')
        categories = Category.objects.all().prefetch_related('subcategories')
        
        # Search functionality
        search_query = request.GET.get('search', '').strip()
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        
        # Filter by category
        category = request.GET.get('category', '').strip()
        if category:
            valid_categories = [choice[0] for choice in Category.CATEGORY_CHOICES]
            if category in valid_categories:
                products = products.filter(category__name=category)
        
        # Filter by subcategory
        subcategory = request.GET.get('subcategory', '').strip()
        if subcategory:
            valid_subcategories = [choice[0] for choice in Subcategory.SUBCATEGORY_CHOICES]
            if subcategory in valid_subcategories:
                products = products.filter(subcategory__name=subcategory)
        
        return render(request, 'employee_admin/products.html', {
            'products': products,
            'categories': categories,
            'current_category': category,
            'current_subcategory': subcategory,
            'search_query': search_query,
            'is_superuser': request.user.is_superuser
        })
    except Exception:
        return render(request, 'employee_admin/products.html', {
            'products': [],
            'categories': [],
            'current_category': '',
            'current_subcategory': '',
            'search_query': '',
            'is_superuser': False
        })


#Admin Orders page
@staff_required
def admin_orders(request):
    try:
        orders = Order.objects.select_related('user').order_by('-created_at')
        
        # Filter by status
        status = request.GET.get('status', '').strip()
        if status:
            valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
            if status in valid_statuses:
                orders = orders.filter(status=status)
        
        return render(request, 'employee_admin/orders.html', {
            'orders': orders,
            'current_status': status,
            'status_choices': Order.STATUS_CHOICES
        })
    except Exception:
        return render(request, 'employee_admin/orders.html', {
            'orders': [],
            'current_status': '',
            'status_choices': []
        })


#Admin add product to database function and relevant error messages
@staff_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                product = form.save(commit=False)
                product.created_by = request.user
                product.save()
                messages.success(request, f'Product "{product.name}" has been added successfully!')
                return redirect('employee_admin:products')
            except Exception:
                messages.error(request, 'Unable to add product. Please try again.')
    else:
        form = ProductForm()
    
    return render(request, 'employee_admin/add_product.html', {'form': form})


#Admin edit product function and relevant error messages
@staff_required
def edit_product(request, pk):
    try:
        pk = int(pk)
        product = get_object_or_404(Product, pk=pk)
        
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, f'Product "{product.name}" has been updated successfully!')
                    return redirect('employee_admin:products')
                except Exception:
                    messages.error(request, 'Unable to update product. Please try again.')
        else:
            form = ProductForm(instance=product)
        
        return render(request, 'employee_admin/edit_product.html', {
            'form': form,
            'product': product
        })
    except (ValueError, TypeError):
        messages.error(request, 'Invalid product ID.')
        return redirect('employee_admin:products')


#Admin delete product function and relevant error messages
@staff_required
def delete_product(request, pk):
    try:
        #Delete a product by pk
        pk = int(pk) 
        product = get_object_or_404(Product, pk=pk)
        
        # Only allow deletion if user is superuser or created the product
        if not request.user.is_superuser and product.created_by != request.user:
            messages.error(request, 'You can only delete products you created.')
            return redirect('employee_admin:products')
        
        if request.method == 'POST':
            try:
                product_name = product.name
                # Delete the image file if product has one
                if product.image:
                    image_path = product.image.path
                    if os.path.exists(image_path):
                        os.remove(image_path)
                product.delete()
                messages.success(request, f'Product "{product_name}" has been deleted successfully!')
            except Exception:
                messages.error(request, 'Unable to delete product. Please try again.')
            return redirect('employee_admin:products')
        
        # render confirmation page
        return render(request, 'employee_admin/delete_product.html', {'product': product})
    except (ValueError, TypeError):
        messages.error(request, 'Invalid product ID.')
        return redirect('employee_admin:products')


#Edit order by pk
@staff_required
def edit_order(request, pk):
    try:
        pk = int(pk)
        order = get_object_or_404(Order, pk=pk)
        
        if request.method == 'POST':
            form = OrderForm(request.POST, instance=order)
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, f'Order {order.order_number} has been updated successfully!')
                    return redirect('employee_admin:orders')
                except Exception:
                    messages.error(request, 'Unable to update order. Please try again.')
        else:
            form = OrderForm(instance=order)
        
        return render(request, 'employee_admin/edit_order.html', {
            'form': form,
            'order': order
        })
    except (ValueError, TypeError):
        messages.error(request, 'Invalid order ID.')
        return redirect('employee_admin:orders')