from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager
from django.utils.timezone import now
from datetime import timedelta
from django.conf import settings

class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    employee_number = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    status_FK = models.ForeignKey('Status', on_delete=models.CASCADE, null=True)
    question_list_FK = models.ForeignKey('QuestionList', on_delete=models.CASCADE, null=True)
    roles_FK = models.ForeignKey('Roles', on_delete=models.CASCADE, null=True)
    modules_FK = models.ForeignKey('Modules', on_delete=models.CASCADE, null=True)

    username = None  # Completely remove the username field

    USERNAME_FIELD = 'employee_number'  # Use employee_number as the primary field for authentication
    REQUIRED_FIELDS = ['email']  # Superuser must provide email

    objects = UserManager()

    
    
class Roles(models.Model):
    role_name = models.CharField(max_length=255)

class Status(models.Model):
    status_name = models.CharField(max_length=255)

class QuestionList(models.Model):
    questions_FK = models.ForeignKey('Questions', on_delete=models.CASCADE, null=True)
    
class Questions(models.Model):
    question_desc = models.CharField(max_length=255)

class Modules(models.Model):
    module_assign = models.CharField(max_length=255)

class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    

class Token(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use the custom user model
        on_delete=models.CASCADE,
        related_name="tokens"
    )
    key = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user}"