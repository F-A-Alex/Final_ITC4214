from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Wishlist
from store.models import Product


#Add to wishlist/Remove only if logged in
@login_required
def add_to_wishlist(request, product_id):
    try:
        product_id = int(product_id)
        product = get_object_or_404(Product, id=product_id, is_active=True)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        
        #if already in wishlist then remove else add
        if product in wishlist.products.all():
            wishlist.products.remove(product)
            messages.info(request, f'{product.name} removed from wishlist.')
        else:
            wishlist.products.add(product)
            messages.success(request, f'{product.name} added to wishlist.')
        
        # Get the referer URL to redirect back to the same page
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        else:
            return redirect('store:product_list')
    except (ValueError, TypeError):
        messages.error(request, 'Invalid product.')
        return redirect('store:product_list')
    except Exception:
        messages.error(request, 'Unable to update wishlist.')
        return redirect('store:product_list')


#Render wishlist page and populate if exists
@login_required
def wishlist_view(request):
    try:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        return render(request, 'wishlist/wishlist.html', {'wishlist': wishlist})
    except Exception:
        return render(request, 'wishlist/wishlist.html', {'wishlist': None})