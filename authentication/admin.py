from django.contrib import admin
from .models import Employee
from .forms import EmployeeCreationForm
from .emails import send_onboarding_email

class EmployeeAdmin(admin.ModelAdmin):
    form = EmployeeCreationForm
    list_display = ('username', 'email', 'first_name', 'last_name', 'account_status', 'role')
    search_fields = ['username', 'email']
    list_filter = ['role', 'account_status']

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        
        if is_new:
            # Automatically assign 'system_admin' role if the user is a superuser
            if obj.is_superuser:
                obj.role = 'system_admin'
            else:
                obj.role = 'employee'  # Regular users get 'employee' role
            super().save_model(request, obj, form, change)

            # Send onboarding email for new regular users
            if not obj.is_superuser:
                send_onboarding_email(request, obj)
        else:
            # If the account is not new and email is changed, don't send onboarding email
            if obj.email != form.initial.get('email'):
                # Here you could choose to notify the user of the email change
                pass

            super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        # Prevent non-superusers from changing the 'role' field
        if not request.user.is_superuser:
            return self.readonly_fields + ('role',)
        return self.readonly_fields

    def has_change_permission(self, request, obj=None):
        # Prevent non-superusers from changing the role if it's a system admin
        if obj and obj.role == 'system_admin' and not request.user.is_superuser:
            return False
        return super().has_change_permission(request, obj)

    def get_list_display_links(self, request, list_display):
        # Disable link for pending accounts
        return ('username',) if not request.GET.get('account_status') == 'pending' else None

admin.site.register(Employee, EmployeeAdmin)
