from django.contrib.auth.models import AbstractUser, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from .managers import UserManager
from django.conf import settings
import uuid

class User(AbstractUser):
    email = models.EmailField(unique=True)
    employee_number = models.CharField(max_length=255, unique=True, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    # Relationships
    status = models.ForeignKey(
        'Status', on_delete=models.SET_NULL, null=True, blank=True, related_name="users"
    )
    role = models.ForeignKey(
        'Role', on_delete=models.SET_NULL, null=True, blank=True, related_name="users"
    )
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

    def save(self, *args, **kwargs):
        # ✅ Ensure job_title is always assigned for Super Admins
        if not self.job_title and self.role and self.role.role_name == "Super Admin":
            super_admin_title, created = JobTitle.objects.get_or_create(title_name="Super Admin")
            if not self.job_title == super_admin_title:  # ✅ Prevent infinite loop
                self.job_title = super_admin_title

        # ✅ Auto-generate employee number (Ensure these methods exist in UserManager)
        if not self.employee_number:
            if self.role and self.role.role_name == "Super Admin":
                self.employee_number = self.objects.generate_super_admin_code()  # Ensure this method exists
            else:
                role_name = self.role.role_name if self.role else None
                self.employee_number = self.objects.generate_employee_number(role_name, self.module)  # Ensure this method exists

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee_number} - {self.first_name} {self.last_name} - {self.email}"

    class Meta:
        db_table = "authentication_user"  # ✅ Avoid conflicts with Django’s auth_user

class Role(models.Model):
    role_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.role_name

class Status(models.Model): 
    status_name = models.CharField(max_length=50, unique=True)

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

class JobTitle(models.Model):
    title_name = models.CharField(max_length=255, unique=True)
    permissions = models.ManyToManyField(
        Permission,  # ✅ Use Django's built-in Permission model
        related_name="job_titles",
        blank=True
    )  

    def __str__(self):
        return self.title_name


class Token(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tokens"
    )
    key = models.CharField(max_length=255, unique=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.employee_number}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
