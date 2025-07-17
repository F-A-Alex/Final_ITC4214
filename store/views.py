from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Min, Max
from django.http import Http404
from .models import Product, Category, Subcategory, get_similar_products
from cart.models import Cart, CartItem
from wishlist.models import Wishlist
from reviews.views import get_product_reviews, get_product_rating_stats

#Render home page with featured products
def home(request):
    try:
        featured_products = Product.objects.filter(
            featured=True, 
            is_active=True
        ).select_related('category', 'subcategory')[:6]
        categories = Category.objects.all().prefetch_related('subcategories')
        return render(request, 'store/home.html', {
            'featured_products': featured_products,
            'categories': categories
        })
    except Exception:
        return render(request, 'store/home.html', {
            'featured_products': [],
            'categories': []
        })


#All Products page view
def product_list(request):
    try:
        products = Product.objects.filter(is_active=True).select_related('category', 'subcategory')
        categories = Category.objects.all().prefetch_related('subcategories')
        
        # Filter by category
        category = request.GET.get('category', '').strip()
        if category:
            try:
                category_obj = Category.objects.get(name=category)
                products = products.filter(category=category_obj)
            except Category.DoesNotExist:
                category = ''
        
        # Filter by subcategory
        subcategory = request.GET.get('subcategory', '').strip()
        if subcategory:
            try:
                subcategory_obj = Subcategory.objects.get(name=subcategory)
                products = products.filter(subcategory=subcategory_obj)
            except Subcategory.DoesNotExist:
                subcategory = ''
        
        # Price filtering
        min_price = request.GET.get('min_price', '').strip()
        max_price = request.GET.get('max_price', '').strip()
        
        if min_price:
            try:
                min_price_val = float(min_price)
                if min_price_val >= 0:
                    products = products.filter(price__gte=min_price_val)
            except (ValueError, TypeError):
                min_price = ''
        
        if max_price:
            try:
                max_price_val = float(max_price)
                if max_price_val >= 0:
                    products = products.filter(price__lte=max_price_val)
            except (ValueError, TypeError):
                max_price = ''
        
        # Search functionality
        search_query = request.GET.get('search', '').strip()
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        
        # Get price range for filter display
        all_products = Product.objects.filter(is_active=True)
        price_range = all_products.aggregate(
            min_price=Min('price'),
            max_price=Max('price')
        )
        if not price_range['min_price']:
            price_range = {'min_price': 0, 'max_price': 1000}
        
        # Get current category object for subcategory filtering
        current_category_obj = None
        if category:
            try:
                current_category_obj = Category.objects.get(name=category)
            except Category.DoesNotExist:
                pass
        
        return render(request, 'store/product_list.html', {
            'products': products,
            'categories': categories,
            'current_category': category,
            'current_category_obj': current_category_obj,
            'current_subcategory': subcategory,
            'search_query': search_query,
            'min_price': min_price,
            'max_price': max_price,
            'price_range': price_range
        })
    except Exception:
        return render(request, 'store/product_list.html', {
            'products': [],
            'categories': [],
            'current_category': '',
            'current_category_obj': None,
            'current_subcategory': '',
            'search_query': '',
            'min_price': '',
            'max_price': '',
            'price_range': {'min_price': 0, 'max_price': 1000}
        })


#Product detail page -render wishlist or cart if authenticated, reviews if exist, similar products
def product_detail(request, pk):
    try:
        pk = int(pk)
        product = get_object_or_404(
            Product.objects.select_related('category', 'subcategory'), 
            pk=pk, 
            is_active=True
        )
        
        # Check if user is authenticated and get cart/wishlist status
        in_wishlist = False
        cart_quantity = 0
        cart_item_id = None
        user_review = None
        
        if request.user.is_authenticated:
            # Check if product is in wishlist
            try:
                wishlist = Wishlist.objects.get(user=request.user)
                in_wishlist = product in wishlist.products.all()
            except Wishlist.DoesNotExist:
                in_wishlist = False
            
            # Check if product is in cart and get quantity
            try:
                cart = Cart.objects.get(user=request.user)
                try:
                    cart_item = CartItem.objects.get(cart=cart, product=product)
                    cart_quantity = cart_item.quantity
                    cart_item_id = cart_item.id
                except CartItem.DoesNotExist:
                    cart_quantity = 0
                    cart_item_id = None
            except (Cart.DoesNotExist, CartItem.DoesNotExist):
                cart_quantity = 0
                cart_item_id = None
            
            # Check if user has reviewed this product
            try:
                from reviews.models import Review
                user_review = Review.objects.get(product=product, user=request.user)
            except Review.DoesNotExist:
                user_review = None
        
        
        # Get similar products
        similar_products = get_similar_products(product, limit=4)
        
        # Get reviews and rating stats
        reviews = get_product_reviews(product, limit=10)
        rating_stats = get_product_rating_stats(product)
        
        return render(request, 'store/product_detail.html', {
            'product': product,
            'similar_products': similar_products,
            'in_wishlist': in_wishlist,
            'cart_quantity': cart_quantity,
            'cart_item_id': cart_item_id,
            'user_review': user_review,
            'reviews': reviews,
            'rating_stats': rating_stats,
        })
    except (ValueError, TypeError):
        raise Http404("Product not found")

def about(request):
    return render(request, 'store/about.html')

def custom_404(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_500(request):
    return render(request, 'errors/500.html', status=500)

def custom_403(request, exception):
    return render(request, 'errors/403.html', status=403)
   