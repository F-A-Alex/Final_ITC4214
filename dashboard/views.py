from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from store.models import  Order
from cart.models import Cart
from wishlist.models import Wishlist


# Get user statistics for dashboard - orders, cart and wishlist
@login_required
def user_dashboard(request):
    try:
        
        user_orders = Order.objects.filter(user=request.user)
        recent_orders = user_orders[:5]
        active_orders = user_orders.exclude(status__in=['delivered', 'cancelled']).count()
        
        cart, _ = Cart.objects.get_or_create(user=request.user)
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        
        context = {
            'total_orders': user_orders.count(),
            'active_orders': active_orders,
            'recent_orders': recent_orders,
            'cart_items': cart.total_items,
            'wishlist_items': wishlist.total_items,
        }
        
        return render(request, 'dashboard/user_dashboard.html', context)
    except Exception:
        return render(request, 'dashboard/user_dashboard.html', {
            'total_orders': 0,
            'active_orders': 0,
            'recent_orders': [],
            'cart_items': 0,
            'wishlist_items': 0,
        })
