from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    path('wishlist/', views.wishlist_view, name='view'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add'),
]