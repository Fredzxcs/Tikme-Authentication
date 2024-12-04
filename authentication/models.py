from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
import secrets


class Employee(AbstractUser):
    ACCOUNT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
    ]

    security_question_1 = models.CharField(max_length=255, blank=True, null=True)
    security_answer_1 = models.CharField(max_length=255, blank=True, null=True)
    security_question_2 = models.CharField(max_length=255, blank=True, null=True)
    security_answer_2 = models.CharField(max_length=255, blank=True, null=True)
    security_question_3 = models.CharField(max_length=255, blank=True, null=True)
    security_answer_3 = models.CharField(max_length=255, blank=True, null=True)
    account_setup_complete = models.BooleanField(default=False)
    account_status = models.CharField(
        max_length=50,
        choices=ACCOUNT_STATUS_CHOICES,
        default='pending',
    )
    role = models.CharField(
        max_length=50,
        choices=[('system_admin', 'System Admin'), ('employee', 'Employee')],
        default='employee',
    )

    job_title = models.CharField(max_length=255, blank=True, null=True)

    def is_system_admin(self):
        return self.role == 'system_admin'

    def is_employee(self):
        return self.role == 'employee'

    def __str__(self):
        return self.username


class Token(models.Model):
    user = models.ForeignKey(Employee, on_delete=models.CASCADE)  # Use Employee model
    token = models.CharField(max_length=255, unique=True)
    expiration_time = models.DateTimeField()
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"Token for {self.user.username}"

    @classmethod
    def generate_token(cls, user, expiration_hours=1):
        """
        Generates a token for the user with a customizable expiration time (default 1 hour).
        """
        token_string = secrets.token_urlsafe(32)  # Generates a secure token
        expiration_time = timezone.now() + timedelta(hours=expiration_hours)
        
        # Create and return the token instance
        return cls.objects.create(user=user, token=token_string, expiration_time=expiration_time)

    def is_expired(self):
        """
        Checks whether the token has expired.
        """
        return self.expiration_time < timezone.now()

    def mark_as_used(self):
        """
        Marks the token as used.
        """
        self.used = True
        self.save()
