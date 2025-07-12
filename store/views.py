from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import Http404
from .models import Product, Category

def home(request):
    try:
        featured_products = Product.objects.filter(
            featured=True, 
            is_active=True
        ).select_related('category')[:6]
        categories = Category.objects.all()
        return render(request, 'store/home.html', {
            'featured_products': featured_products,
            'categories': categories
        })
    except Exception:
        return render(request, 'store/home.html', {
            'featured_products': [],
            'categories': []
        })

def product_list(request):
    try:
        products = Product.objects.filter(is_active=True).select_related('category')
        categories = Category.objects.all()
        
        # Filter by category with validation
        category = request.GET.get('category', '').strip()
        if category:
            # Validate category exists
            valid_categories = [choice[0] for choice in Category.CATEGORY_CHOICES]
            if category in valid_categories:
                products = products.filter(category__name=category)
        
        # Search functionality
        search_query = request.GET.get('search', '').strip()
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        
        return render(request, 'store/product_list.html', {
            'products': products,
            'categories': categories,
            'current_category': category,
            'search_query': search_query
        })
    except Exception:
        return render(request, 'store/product_list.html', {
            'products': [],
            'categories': [],
            'current_category': '',
            'search_query': ''
        })

def product_detail(request, pk):
    try:
        pk = int(pk)
        product = get_object_or_404(
            Product.objects.select_related('category'), 
            pk=pk, 
            is_active=True
        )
        related_products = Product.objects.filter(
            category=product.category, 
            is_active=True
        ).exclude(pk=pk).select_related('category')[:4]
        
        return render(request, 'store/product_detail.html', {
            'product': product,
            'related_products': related_products
        })
    except (ValueError, TypeError):
        raise Http404("Product not found")

def custom_404(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_500(request):
    return render(request, 'errors/500.html', status=500)

def custom_403(request, exception):
    return render(request, 'errors/403.html', status=403)