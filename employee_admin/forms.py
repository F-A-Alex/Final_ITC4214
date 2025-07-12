from django import forms
from django.core.exceptions import ValidationError
from store.models import Product, Order

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'image', 'stock_quantity', 'is_active', 'featured']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            'stock_quantity': forms.NumberInput(attrs={'min': '0'}),
            'image': forms.FileInput(attrs={'accept': 'image/*'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['price'].widget.attrs.update({'class': 'form-control'})
        self.fields['category'].widget.attrs.update({'class': 'form-select'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})
        self.fields['stock_quantity'].widget.attrs.update({'class': 'form-control'})
        self.fields['is_active'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['featured'].widget.attrs.update({'class': 'form-check-input'})
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Handle both file objects and strings
            if hasattr(image, 'size'):
                file_size = image.size
            elif hasattr(image, 'file') and hasattr(image.file, 'size'):
                file_size = image.file.size
            else:
                # If we can't determine size, skip size check
                file_size = 0
            
            # Check file size (5MB limit)
            if file_size > 5 * 1024 * 1024:
                raise ValidationError("Image file too large. Maximum size is 5MB.")
            
            # Check file type
            if hasattr(image, 'name') and image.name:
                valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
                if not any(image.name.lower().endswith(ext) for ext in valid_extensions):
                    raise ValidationError("Invalid image format. Please use JPG, PNG, GIF, or WebP.")
        
        return image

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', 'shipping_address']
        widgets = {
            'shipping_address': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget.attrs.update({'class': 'form-select'})
        self.fields['shipping_address'].widget.attrs.update({'class': 'form-control'})