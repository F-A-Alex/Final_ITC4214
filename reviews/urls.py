from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('reviews/add/<int:product_id>/', views.add_review, name='add'),
    path('reviews/delete/<int:review_id>/', views.delete_review, name='delete'),
]