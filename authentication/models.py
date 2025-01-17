from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager
from django.conf import settings


class User(AbstractUser):
    # Removed 'name' field and replaced it with 'first_name' and 'last_name' only
    email = models.EmailField(unique=True)
    employee_number = models.CharField(max_length=255, unique=True)

    # Relationships
    status = models.ForeignKey(
        'Status', on_delete=models.SET_NULL, null=True, blank=True, related_name="users"
    )
    question_list = models.ForeignKey(
        'QuestionList', on_delete=models.SET_NULL, null=True, blank=True, related_name="users"
    )
    role = models.ForeignKey(
        'Role', on_delete=models.CASCADE, null=True, related_name="users"
    )  # Critical relationship for role-based access
    module = models.ForeignKey(
        'Module', on_delete=models.CASCADE, null=True, blank=True, related_name="users"
    )
    job_title = models.ForeignKey(
        'JobTitle', on_delete=models.SET_NULL, null=True, blank=True, related_name="users"
    )

    # Remove username and use employee_number for authentication
    username = None
    USERNAME_FIELD = 'employee_number'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    objects = UserManager()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee_number} - {self.first_name} {self.last_name}"


class Role(models.Model):
    role_name = models.CharField(max_length=50, unique=True)
    permissions = models.ManyToManyField(
        'Permission', related_name="roles", blank=True
    )

    def __str__(self):
        return self.role_name


class Status(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    )
    status_name = models.CharField(max_length=50, unique=True, choices=STATUS_CHOICES)

    def __str__(self):
        return self.status_name


class QuestionList(models.Model):
    questions = models.ManyToManyField('Question', related_name="question_lists")

    def __str__(self):
        return f"Question List {self.id}"


class Question(models.Model):
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.description


class Module(models.Model):
    module_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.module_name


class Permission(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class JobTitle(models.Model):
    title_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.title_name


class Token(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tokens"
    )
    key = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.employee_number}"
