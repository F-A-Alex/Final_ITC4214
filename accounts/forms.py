from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile
import re
from datetime import date, timedelta

# Registration Form for Users 
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    

    #Validations to check if user wth same email or username already exists
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if User.objects.filter(email=email).exists():
                raise ValidationError("A user with this email already exists.")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise ValidationError("A user with this username already exists. Please choose a different username.")
        return username
    
    #Save function
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

#Form to update the two user fields in the user model - for edit profile page 
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your last name'
            }),
        }

#Form to update the rest of the fields in the profile model - for edit profile page 
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number', 'address', 'city', 'postal_code', 'country', 'date_of_birth']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890 or 1234567890',
                'required': False  
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter your full address',
                'required': False  
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your city',
                'required': False  
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12345 or A1B 2C3',
                'required': False 
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your country',
                'required': False 
            }),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set max date to today cant have birthday in future
        self.fields['date_of_birth'].widget.attrs['max'] = date.today().isoformat()

        # Add help text to some fields
        self.fields['phone_number'].help_text = "Format: +1234567890 or 1234567890"
        self.fields['postal_code'].help_text = "Format: 12345 or A1B 2C3"
        self.fields['address'].help_text = "Maximum 500 characters"
    

    def __init__(self, *args, **kwargs):
        # Check if this is being used for checkout
        self.for_checkout = kwargs.pop('for_checkout', False)
        super().__init__(*args, **kwargs)
        
        # Set max date to today cant have birthday in future
        self.fields['date_of_birth'].widget.attrs['max'] = date.today().isoformat()

        # Add help text to some fields
        self.fields['phone_number'].help_text = "Format: +1234567890 or 1234567890"
        self.fields['postal_code'].help_text = "Format: 12345 or A1B 2C3"
        self.fields['address'].help_text = "Maximum 500 characters"
        
        # Since reusing the same form and model - if used for checkout, make fields required 
        if self.for_checkout:
            self.fields['phone_number'].required = True
            self.fields['address'].required = True
            self.fields['city'].required = True
            self.fields['postal_code'].required = True
            self.fields['country'].required = True
            self.fields['phone_number'].widget.attrs['required'] = True
            self.fields['address'].widget.attrs['required'] = True
            self.fields['city'].widget.attrs['required'] = True
            self.fields['postal_code'].widget.attrs['required'] = True
            self.fields['country'].widget.attrs['required'] = True

    #Some extra validation checks and restrictions
    # Phone field with relevant error messages
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        if phone:
            # Remove spaces and hyphens
            clean_phone = re.sub(r'[\s\-]', '', phone)
            if not re.match(r'^\+?1?\d{9,15}$', clean_phone):
                raise ValidationError("Enter a valid phone number (9-15 digits, optionally starting with + or country code).")
        return phone
    

    #DOB validation and legal age restriction
    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            #This shouldnt ever show up due to earlier restriction but just in case will print message as well
            if dob > date.today():
                raise ValidationError("Date of birth cannot be in the future.")
            
            # Check if user is at least 13 years old - just to have some checks to be sure user can order legally 
            min_age_date = date.today() - timedelta(days=13*365)
            if dob > min_age_date:
                raise ValidationError("You must be at least 13 years old to register.")
        
        return dob