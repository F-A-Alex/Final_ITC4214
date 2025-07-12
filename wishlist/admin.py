from django.contrib import admin
from .models import Wishlist

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_items', 'created_at']
    filter_horizontal = ['products']
    readonly_fields = ['created_at', 'updated_at']