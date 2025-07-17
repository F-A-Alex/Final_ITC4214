from store.models import Product
from .models import Cart


#Recommendation function based on similar products in the cart 
def get_cart_recommendations(user, limit=4):
    try:
        cart = Cart.objects.get(user=user)

        #Get products in cart or check if empty
        cart_products = [item.product for item in cart.items.all() if item.product]
        if not cart_products:
            return Product.objects.none()
        
        # Collect unique categories and subcategories from the cart items
        categories = set(p.category for p in cart_products if p.category)
        subcategories = set(p.subcategory for p in cart_products if p.subcategory)

        #Get the ids of produts already in cart so dont recommend same items
        cart_product_ids = [p.id for p in cart_products]

        # Get subcategory matches first
        subcategory_qs = Product.objects.filter(
            subcategory__in=subcategories,
            is_active=True
        ).exclude(id__in=cart_product_ids).select_related('category', 'subcategory')

        recommendations = list(subcategory_qs[:limit])


        #If not enough items to display in same subcategory then show category matches
        if len(recommendations) < limit:
            category_qs = Product.objects.filter(
                category__in=categories,
                is_active=True
            ).exclude(id__in=cart_product_ids).exclude(id__in=[p.id for p in recommendations]).select_related('category', 'subcategory')

            needed = limit - len(recommendations)
            recommendations += list(category_qs[:needed])

        return recommendations

    except Cart.DoesNotExist:
        return Product.objects.none()
    except Exception:
        return Product.objects.none()


