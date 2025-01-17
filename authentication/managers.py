from django.contrib.auth.models import BaseUserManager
from django.apps import apps  # Import apps to dynamically load models


class UserManager(BaseUserManager):
    """
    Custom manager for the User model.
    """

    def create_user(self, employee_number, email, password=None, **extra_fields):
        """
        Creates and returns a regular user with the given details.
        """
        if not employee_number:
            raise ValueError('The Employee Number must be set')
        if not email:
            raise ValueError('The Email must be set')

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

    def create_superuser(self, employee_number, email, password=None, **extra_fields):
        """
        Creates and returns a superuser with the given details.
        Automatically assigns the 'Super Admin' role and 'Active' status.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # Dynamically fetch the Role and Status models to avoid circular imports
        Role = apps.get_model('authentication', 'Role')
        Status = apps.get_model('authentication', 'Status')

        # Set the role to 'Super Admin' if not already provided
        if not extra_fields.get('role'):
            extra_fields['role'], _ = Role.objects.get_or_create(role_name='Super Admin')

        # Set the status to 'Active' if not already provided
        if not extra_fields.get('status'):
            extra_fields['status'], _ = Status.objects.get_or_create(status_name='Active')

        # Super Admin does not require a module
        extra_fields['module'] = None

        return self.create_user(employee_number, email, password, **extra_fields)
