from django.contrib.auth.models import BaseUserManager
from django.apps import apps  # Import apps to dynamically load models
import random

class UserManager(BaseUserManager):

    def generate_unique_employee_number(self, prefix, length=4):
        """ Generate a unique employee number ensuring it does not exist in the database """
        from .models import User  # Import inside function to avoid circular imports

        while True:
            random_number = random.randint(1000, 9999)
            employee_number = f"{prefix}-{random_number}"
            if not User.objects.filter(employee_number=employee_number).exists():
                return employee_number

    def generate_super_admin_code(self):
        """ Generate a unique employee number for Super Admins """
        return self.generate_unique_employee_number("SUP")

    def generate_employee_number(self, role=None, module=None):
        """ Generate employee number based on role and module """
        if role == "Super Admin":
            return self.generate_super_admin_code()
        elif role == "System Admin":
            return self.generate_unique_employee_number("SYS")
        elif module:
            module_prefix = module.module_name[:3].upper()
            return self.generate_unique_employee_number(f"{role[:3].upper()}-{module_prefix}")
        return self.generate_unique_employee_number(f"{role[:3].upper()}-GEN")

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and returns a regular user with the given details.
        """
        if not email:
            raise ValueError('The Email must be set')

        Role = apps.get_model('authentication', 'Role')
        Module = apps.get_model('authentication', 'Module')

        role = extra_fields.get('role')
        module = extra_fields.get('module')

        if isinstance(role, Role):
            role_name = role.role_name
        else:
            role_name = role  # Assume it's a string

        if isinstance(module, Module):
            module_name = module.module_name
        else:
            module_name = module  # Assume it's a string

        # Auto-generate employee number if not provided
        employee_number = self.generate_employee_number(role_name, module_name)

        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        user = self.model(
            employee_number=employee_number,
            email=self.normalize_email(email),
            **extra_fields
        )
        if password:
            user.set_password(password)
        else:
            raise ValueError("Password must be set.")
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        Role = apps.get_model('authentication', 'Role')
        Status = apps.get_model('authentication', 'Status')

        # Set role and status for Super Admin
        extra_fields['role'], _ = Role.objects.get_or_create(role_name='Super Admin')
        extra_fields['status'], _ = Status.objects.get_or_create(status_name='Active')

        # Super Admin does not require a module
        extra_fields['module'] = None

        # Ensure auto-generated employee number
        employee_number = self.generate_super_admin_code()

        # Remove 'employee_number' from extra_fields to prevent duplicate argument error
        extra_fields.pop('employee_number', None)

        # Create user
        user = self.model(
            employee_number=employee_number,
            email=self.normalize_email(email),
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        # ✅ PRINT the generated employee_number so it's visible in the terminal
        print(f"\n✅ Super Admin Created Successfully!\nEmployee Number: {employee_number}\n")

        return user




    def get_by_natural_key(self, employee_number):
        """
        Ensures that Django's authentication system correctly retrieves users by employee_number.
        """
        return self.get(employee_number=employee_number)

    def get_input_fields(self, user, **kwargs):
        """
        This ensures that Django does not prompt for employee_number during createsuperuser.
        """
        fields = super().get_input_fields(user, **kwargs)
        return [field for field in fields if field != "employee_number"]
