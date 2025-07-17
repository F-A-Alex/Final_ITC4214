from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from PIL import Image
import uuid


#Get products similar to the given product 
def get_similar_products(product, limit=4):
    try:
        # First: products from same subcategory
        similar_products = list(Product.objects.filter(
            subcategory=product.subcategory,
            is_active=True
        ).exclude(pk=product.pk).select_related('category', 'subcategory'))

        # If not enough, add products from same category
        if len(similar_products) < limit:
            additional_products = list(Product.objects.filter(
                category=product.category,
                is_active=True
            ).exclude(pk=product.pk).exclude(pk__in=[p.pk for p in similar_products])
            .select_related('category', 'subcategory'))

            similar_products += additional_products

        return similar_products[:limit]
    except Exception:
        return Product.objects.none()


#Category model
class Category(models.Model):
    CATEGORY_CHOICES = [
        ('decorations', 'Decorations'),
        ('jewelry', 'Jewelry'),
    ]
    
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.get_name_display()

#Subcategory model
class Subcategory(models.Model):
    SUBCATEGORY_CHOICES = [
        ('pottery', 'Pottery'),
        ('wood', 'Wood Items'),
        ('necklaces', 'Necklaces'),
        ('earrings', 'Earrings'),
    ]
    
    name = models.CharField(max_length=50, choices=SUBCATEGORY_CHOICES, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Subcategories"
        unique_together = ('name', 'category')
    
    def __str__(self):
        return self.get_name_display()

#Product model
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    image = models.ImageField(upload_to='products/', default='products/default.jpg') #upload to media directory  
    stock_quantity = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(9999)]
    )
    is_active = models.BooleanField(default=True) #is active on website
    featured = models.BooleanField(default=False) #is featured on home page
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['subcategory', 'is_active']),
            models.Index(fields=['featured', 'is_active']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
            models.Index(fields=['created_by']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('store:product_detail', kwargs={'pk': self.pk})
    
    def clean(self):
        if self.subcategory and self.category:
            if self.subcategory.category != self.category:
                raise ValidationError("Subcategory must belong to the selected category.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 800 or img.width > 800:
                output_size = (800, 800)
                img.thumbnail(output_size)
                img.save(self.image.path)


#Orders model
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


#Order Model individual
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['order', 'product']),
        ]
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def total_price(self):
        return self.quantity * self.price