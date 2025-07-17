from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

# Unregister the default User admin first so we can add extra fields
admin.site.unregister(User)

# Custom User admin with staff management
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    
    fieldsets = list(BaseUserAdmin.fieldsets)
    for name, opts in fieldsets:
    	if 'fields' in opts and 'is_staff' in opts['fields']:
            opts['description'] = 'Staff members can access the employee admin dashboard and manage products.'
            break
    fieldsets = tuple(fieldsets)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.none()  # Non-superusers can't manage users
    
    def has_module_permission(self, request):
        return request.user.is_superuser

# Register the custom User admin
admin.site.register(User, UserAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'city', 'country']
    search_fields = ['user__username', 'user__email', 'phone_number']
    list_filter = ['city', 'country']
