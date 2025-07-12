from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Cart, CartItem
from store.models import Product, Order, OrderItem

@login_required
def add_to_cart(request, product_id):
    try:
        product_id = int(product_id)
        product = get_object_or_404(Product, id=product_id, is_active=True)
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )
        
        if not created:
            if cart_item.quantity < product.stock_quantity:
                cart_item.quantity += 1
                cart_item.save()
                message = f'{product.name} quantity updated in cart.'
            else:
                messages.warning(request, f'Sorry, only {product.stock_quantity} items available.')
                return redirect(request.META.get('HTTP_REFERER', 'store:product_list'))
        else:
            message = f'{product.name} added to cart.'
        
        messages.success(request, message)
        return redirect(request.META.get('HTTP_REFERER', 'store:product_list'))
    except (ValueError, TypeError):
        messages.error(request, 'Invalid product.')
        return redirect('store:product_list')
    except Exception:
        messages.error(request, 'Unable to add item to cart.')
        return redirect('store:product_list')

@login_required
def cart_view(request):
    try:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return render(request, 'cart/cart.html', {'cart': cart})
    except Exception:
        return render(request, 'cart/cart.html', {'cart': None})

@login_required
@require_POST
def update_cart_item(request, item_id):
    try:
        item_id = int(item_id)
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        if 1 <= quantity <= cart_item.product.stock_quantity:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated successfully.')
        else:
            messages.error(request, 'Invalid quantity.')
    except (ValueError, TypeError):
        messages.error(request, 'Invalid request.')
    except Exception:
        messages.error(request, 'Unable to update cart.')
    
    return redirect('cart:view')

@login_required
def remove_from_cart(request, item_id):
    try:
        item_id = int(item_id)
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        product_name = cart_item.product.name
        cart_item.delete()
        messages.success(request, f'{product_name} removed from cart.')
    except (ValueError, TypeError):
        messages.error(request, 'Invalid request.')
    except Exception:
        messages.error(request, 'Unable to remove item.')
    
    return redirect('cart:view')

@login_required
def checkout(request):
    try:
        cart = get_object_or_404(Cart, user=request.user)
        if not cart.items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('cart:view')
        
        # Check stock availability
        for item in cart.items.all():
            if item.quantity > item.product.stock_quantity:
                messages.error(request, f'Sorry, only {item.product.stock_quantity} of {item.product.name} available.')
                return redirect('cart:view')
        
        if request.method == 'POST':
            shipping_address = request.POST.get('shipping_address', '').strip()
            if not shipping_address:
                messages.error(request, 'Shipping address is required.')
                return render(request, 'cart/checkout.html', {'cart': cart})
            
            try:
                with transaction.atomic():
                    # Create order
                    order = Order.objects.create(
                        user=request.user,
                        total_amount=cart.total_price,
                        shipping_address=shipping_address
                    )
                    
                    # Create order items and update stock
                    for item in cart.items.all():
                        # Double-check stock with select_for_update
                        product = Product.objects.select_for_update().get(id=item.product.id)
                        if item.quantity > product.stock_quantity:
                            raise ValidationError(f'Insufficient stock for {product.name}')
                        
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=item.quantity,
                            price=product.price
                        )
                        
                        # Update stock
                        product.stock_quantity -= item.quantity
                        product.save()
                    
                    # Clear cart
                    cart.items.all().delete()
                    
                    messages.success(request, f'Order {order.order_number} placed successfully!')
                    return redirect('cart:order_confirmed', order_number=order.order_number)
                    
            except ValidationError as e:
                messages.error(request, str(e))
                return redirect('cart:view')
            except Exception:
                messages.error(request, 'Unable to process order. Please try again.')
                return render(request, 'cart/checkout.html', {'cart': cart})
        
        return render(request, 'cart/checkout.html', {'cart': cart})
    except Exception:
        messages.error(request, 'Unable to access checkout.')
        return redirect('cart:view')

@login_required
def order_confirmed(request, order_number):
    try:
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
        return render(request, 'cart/order_confirmed.html', {'order': order})
    except Exception:
        messages.error(request, 'Order not found.')
        return redirect('store:home')