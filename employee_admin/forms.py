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
        
        # Handle subcategory queryset based on form data or instance
        if self.data and self.data.get('category'):
            # Form submission with category selected - show subcategories for selected category
            try:
                category_id = int(self.data.get('category'))
                self.fields['subcategory'].queryset = Subcategory.objects.filter(category_id=category_id)
            except (ValueError, TypeError):
                self.fields['subcategory'].queryset = Subcategory.objects.none()
        elif self.instance and self.instance.pk and self.instance.category:
            # Editing existing product - show subcategories for current category
            self.fields['subcategory'].queryset = Subcategory.objects.filter(category=self.instance.category)
        else:
            # New product form - start with empty subcategories
            self.fields['subcategory'].queryset = Subcategory.objects.none()
        
        # Add data attributes for JavaScript - since using Ajax here
        self.fields['category'].widget.attrs.update({'data-subcategory-url': '/employee-admin/get-subcategories/'})
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        
        # For new products, image is not required but if provided, validate it
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
    

    #Ensure the appropriate subcategory is selected according to categories (so we dont have database issue)
    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        subcategory = cleaned_data.get('subcategory')
        
        if category and subcategory:
            if subcategory.category != category:
                raise ValidationError("The selected subcategory does not belong to the selected category.")
        
        return cleaned_data

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