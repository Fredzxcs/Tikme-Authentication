from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, employee_number, email, password=None, **extra_fields):
        if not employee_number:
            raise ValueError('The Employee Number must be set')
        if not email:
            raise ValueError('The Email must be set')
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        user = self.model(employee_number=employee_number, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, employee_number, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(employee_number, email, password, **extra_fields)
