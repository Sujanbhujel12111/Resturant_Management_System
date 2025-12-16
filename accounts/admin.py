from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django import forms
from django.db import transaction
from .models import Staff, StaffPermission

User = get_user_model()


class StaffPermissionInline(admin.TabularInline):
    """Inline admin for staff permissions with checkboxes"""
    model = StaffPermission
    fields = ('module', 'is_allowed')
    extra = 0
    
    def get_queryset(self, request):
        """Ensure all modules are shown"""
        qs = super().get_queryset(request)
        return qs


class CombinedStaffForm(forms.ModelForm):
    """Combined form for creating User + Staff + Permissions in one go"""
    # User fields
    username = forms.CharField(
        max_length=150,
        help_text='Username for login'
    )
    email = forms.EmailField(
        help_text='Email address'
    )
    first_name = forms.CharField(
        max_length=150,
        required=False,
        help_text='First name (optional)'
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        help_text='Last name (optional)'
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        help_text='Password for login'
    )
    
    # Permission checkboxes
    permissions = forms.MultipleChoiceField(
        choices=StaffPermission.MODULE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Module Permissions',
        help_text='Select which modules this staff can access'
    )
    
    class Meta:
        model = Staff
        fields = ('staff_type', 'role', 'contact', 'salary', 'joined_date', 'is_active')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Reorder fields - put permissions at the end
        if 'permissions' in self.fields:
            # Create new ordered dict with permissions at the end
            field_order = []
            for key in self.fields:
                if key != 'permissions':
                    field_order.append(key)
            field_order.append('permissions')
            
            # Reconstruct fields in correct order
            new_fields = {}
            for key in field_order:
                new_fields[key] = self.fields[key]
            self.fields = new_fields


class EditStaffForm(forms.ModelForm):
    """Simple form for editing existing staff (no user fields needed)"""
    class Meta:
        model = Staff
        fields = ('staff_type', 'role', 'contact', 'salary', 'joined_date', 'is_active')


class StaffInline(admin.StackedInline):
    """Inline admin for Staff model"""
    model = Staff
    can_delete = False
    verbose_name_plural = 'Staff Profile'
    fk_name = 'user'
    extra = 0
    fields = ('staff_type', 'role', 'contact', 'salary', 'joined_date', 'is_active')


# Note: User admin is removed - users are created through Staff creation form only


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    """Combined Staff + User + Permissions admin interface"""
    form = CombinedStaffForm
    list_display = ('get_username', 'get_staff_type', 'role', 'is_active', 'get_permissions_count')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'role')
    list_filter = ('is_active', 'staff_type', 'role', 'joined_date')
    
    def get_inlines(self, request, obj=None):
        """Show permissions inline only when editing existing staff"""
        if obj is not None:  # Editing existing staff
            return (StaffPermissionInline,)
        return ()  # No inlines when creating new staff
    
    def get_form(self, request, obj=None, **kwargs):
        """Use combined form for add, edit form for edit"""
        if obj is None:  # Adding new staff
            return CombinedStaffForm
        else:  # Editing existing staff
            return EditStaffForm
    
    def get_fieldsets(self, request, obj=None):
        """Configure fieldsets based on add vs edit"""
        if obj is None:  # Adding new staff
            return (
                ('👤 User Account', {
                    'fields': ('username', 'email', 'first_name', 'last_name', 'password'),
                    'description': 'Login credentials for the staff member'
                }),
                ('👨‍💼 Staff Details', {
                    'fields': ('staff_type', 'role', 'contact', 'salary', 'joined_date', 'is_active'),
                    'description': 'Staff profile information'
                }),
                ('🔐 Permissions', {
                    'fields': ('permissions',),
                    'description': 'Select which modules this staff can access'
                }),
            )
        else:  # Editing existing staff
            return (
                ('👨‍💼 Staff Details', {
                    'fields': ('staff_type', 'role', 'contact', 'salary', 'joined_date', 'is_active'),
                    'description': 'Staff profile information'
                }),
            )
    
    def save_model(self, request, obj, form, change):
        """Handle creation of User + Staff + Permissions in transaction"""
        if not change:  # Creating new staff
            with transaction.atomic():
                # Create User from form data
                username = form.cleaned_data.get('username')
                email = form.cleaned_data.get('email')
                first_name = form.cleaned_data.get('first_name', '')
                last_name = form.cleaned_data.get('last_name', '')
                password = form.cleaned_data.get('password')
                
                # Create the user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password,
                    role='staff'
                )
                
                # Link user to staff
                obj.user = user
                obj.save()
                
                # Create permissions for all modules
                permissions_list = form.cleaned_data.get('permissions', [])
                for module in StaffPermission.MODULE_CHOICES:
                    module_code = module[0]
                    is_allowed = module_code in permissions_list
                    StaffPermission.objects.create(
                        staff=obj,
                        module=module_code,
                        is_allowed=is_allowed
                    )
        else:
            # Editing existing staff
            obj.save()
    
    def get_username(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_username.short_description = 'Staff Name'
    
    def get_staff_type(self, obj):
        return obj.get_staff_type_display()
    get_staff_type.short_description = 'Staff Type'
    
    def get_permissions_count(self, obj):
        allowed = obj.permissions.filter(is_allowed=True).count()
        total = obj.permissions.count()
        return f"{allowed}/{total} modules"
    get_permissions_count.short_description = 'Module Access'


