from django.urls import path
from . import views

app_name = 'employee_admin'

urlpatterns = [
    path('employee-admin/', views.admin_dashboard, name='dashboard'),
    path('employee-admin/products/', views.admin_products, name='products'),
    path('employee-admin/products/add/', views.add_product, name='add_product'),
    path('employee-admin/products/<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('employee-admin/products/<int:pk>/delete/', views.delete_product, name='delete_product'),
    path('employee-admin/orders/', views.admin_orders, name='orders'),
    path('employee-admin/orders/<int:pk>/edit/', views.edit_order, name='edit_order'),
    path('employee-admin/get-subcategories/', views.get_subcategories, name='get_subcategories'),
]