from django.contrib.auth.models import AbstractUser, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from .managers import UserManager
from django.conf import settings
import uuid

class User(AbstractUser):
    email = models.EmailField(unique=True)
    user_number = models.CharField(max_length=255, unique=True, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    # Relationships
    status = models.ForeignKey('Status', on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
    role = models.ForeignKey('Role', on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
    module = models.ForeignKey('Module', on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
    job_title = models.ForeignKey('JobTitle', on_delete=models.SET_NULL, null=True, blank=True, related_name="users")

    # ✅ Security Questions
    security_question = models.ForeignKey('SecurityQuestion', on_delete=models.SET_NULL, null=True, blank=True)
    security_answer = models.CharField(max_length=255, blank=True, null=True)

    # ✅ Login Attempts & Locking Mechanism
    failed_attempts = models.IntegerField(default=0)  # Track failed logins
    last_failed_attempt = models.DateTimeField(null=True, blank=True)  # Last failed login attempt
    temporary_lock_until = models.DateTimeField(null=True, blank=True)  # Temporary lock expiration time
    is_permanently_locked = models.BooleanField(default=False)  # Track if account is permanently locked

    # Remove username and use user_number for authentication
    username = None
    USERNAME_FIELD = 'user_number'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    objects = UserManager()

    def lock_temporarily(self):
            """ Lock user temporarily for 15 minutes """
            self.temporary_lock_until = now() + timedelta(minutes=15)
            self.failed_attempts = 0  # Reset failed attempts after lock
            self.save()

    def lock_permanently(self):
        """ Permanently lock the user account """
        self.is_permanently_locked = True
        self.save()

    def reset_failed_attempts(self):
        """ Reset failed attempts after successful login """
        self.failed_attempts = 0
        self.temporary_lock_until = None
        self.save()

    def save(self, *args, **kwargs):
        """ Ensure user_number & security question are assigned """
        from .models import SecurityQuestion, JobTitle  # ✅ Prevent circular imports

        # ✅ Assign job title for Super Admin
        if not self.job_title and self.role and self.role.role_name == "Super Admin":
            super_admin_title, _ = JobTitle.objects.get_or_create(title_name="Super Admin")
            self.job_title = super_admin_title

        # ✅ Auto-generate user number if not set
        if not self.user_number:
            if self.role and self.role.role_name == "Super Admin":
                self.user_number = User.objects.generate_super_admin_code()
            else:
                role_name = self.role.role_name if self.role else None
                self.user_number = User.objects.generate_user_number(role_name, self.module)

        # ✅ Assign default security question (Only if it's missing)
        if self.role and self.role.role_name == "Super Admin" and not self.security_question:
            first_question = SecurityQuestion.objects.first()
            if first_question and not self.security_question:  # Prevent overwriting
                self.security_question = first_question

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_number} - {self.first_name} {self.last_name} - {self.email}"
    
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
        return f"{self.user.user_number} - {self.question.question_text}"

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
        return f"Token for {self.user.user_number}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
