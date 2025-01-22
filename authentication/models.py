from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager
from django.conf import settings


class User(AbstractUser):
    email = models.EmailField(unique=True)
    employee_number = models.CharField(max_length=255, unique=True)

    # Relationships
    status = models.ForeignKey(
        'Status', on_delete=models.SET_NULL, null=True, blank=True, related_name="users"
    )
    role = models.ForeignKey(
        'Role', on_delete=models.SET_NULL, null=True, blank=True, related_name="users"
    )  # Fixed `on_delete` to SET_NULL for consistency
    module = models.ForeignKey(
        'Module', on_delete=models.SET_NULL, null=True, blank=True, related_name="users"
    )
    job_title = models.ForeignKey(
        'JobTitle', on_delete=models.SET_NULL, null=True, blank=True, related_name="users"
    )

    # Remove username and use employee_number for authentication
    username = None
    USERNAME_FIELD = 'employee_number'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    objects = UserManager()

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


class SecurityQuestion(models.Model):
    question_text = models.CharField(max_length=255)

    def __str__(self):
        return self.question_text


class SecurityAnswer(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="security_answers")
    question = models.ForeignKey(SecurityQuestion, on_delete=models.CASCADE)
    answer = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'question'], name='unique_user_question')
        ]

    def __str__(self):
        return f"{self.user.employee_number} - {self.question.question_text}"


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
