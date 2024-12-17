from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    employee_number = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username = None
    status_FK = models.ForeignKey('Status', on_delete=models.CASCADE, null=True)
    question_list_FK = models.ForeignKey('QuestionList', on_delete=models.CASCADE, null=True)
    roles_FK = models.ForeignKey('Roles', on_delete=models.CASCADE, null=True)
    modules_FK = models.ForeignKey('Modules', on_delete=models.CASCADE, null=True)

    USERNAME_FIELD = 'employee_number'
    REQUIRED_FIELDS = []
    
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