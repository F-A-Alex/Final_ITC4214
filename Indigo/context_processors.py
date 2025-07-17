from cart.models import Cart
from wishlist.models import Wishlist

#Add cart item count to template context so can access in any template
def cart_count(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            return {'cart_count': cart.total_items}
        except Cart.DoesNotExist:
            return {'cart_count': 0}
    return {'cart_count': 0}

#Add wishlist item count to template context
def wishlist_count(request):
    if request.user.is_authenticated:
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            return {'wishlist_count': wishlist.total_items}
        except Wishlist.DoesNotExist:
            return {'wishlist_count': 0}
    return {'wishlist_count': 0}