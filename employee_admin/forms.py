from django import forms
from django.core.exceptions import ValidationError
from store.models import Product, Subcategory, Order

# Form for creating and updating products
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'subcategory', 'image', 'stock_quantity', 'is_active', 'featured']
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
        self.fields['subcategory'].widget.attrs.update({'class': 'form-select'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})
        self.fields['stock_quantity'].widget.attrs.update({'class': 'form-control'})
        self.fields['is_active'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['featured'].widget.attrs.update({'class': 'form-check-input'})
        
        # Filter subcategories based on category if editing existing product else show all
        if self.instance and self.instance.pk and self.instance.category:
            self.fields['subcategory'].queryset = Subcategory.objects.filter(category=self.instance.category)
        else:
            self.fields['subcategory'].queryset = Subcategory.objects.all()
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        #check for file size or default to 0 so there is no error
        if image:
            if hasattr(image, 'size'):
                file_size = image.size
            elif hasattr(image, 'file') and hasattr(image.file, 'size'):
                file_size = image.file.size
            else:
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

# Form for orders
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget.attrs.update({'class': 'form-select'})