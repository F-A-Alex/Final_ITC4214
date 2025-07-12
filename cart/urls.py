from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('cart/', views.cart_view, name='view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('cart/order-confirmed/<str:order_number>/', views.order_confirmed, name='order_confirmed'),
]