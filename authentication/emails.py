from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.conf import settings
import datetime
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.core.mail import EmailMessage
from django.contrib.staticfiles.storage import staticfiles_storage
from datetime import timedelta
from django.utils import timezone
from .models import Token

def send_onboarding_email(request, employee):
    # Generate a JWT token with an expiration time
    refresh = RefreshToken.for_user(employee)
    access_token = str(refresh.access_token)  # Generate a short-lived JWT token

    # Set a custom expiration time for the token (e.g., 1 day)
    expiration_time = timezone.now() + timedelta(days=1)

    # Create the Token record in the database
    token_record = Token.objects.create(
        user=employee,
        token=access_token,
        expiration_time=expiration_time,
        used=False  # Initially, the token is unused
    )

    # Build the URL for account setup
    uid = urlsafe_base64_encode(force_bytes(employee.pk))
    link = reverse('setup_account', kwargs={'uidb64': uid, 'token': access_token})
    full_link = request.build_absolute_uri(link)

    # Static image URL
    image_url = staticfiles_storage.url('images/tikme-logo.png')

    # Extract the username (assuming your employee object has a username field)
    username = employee.username  # Or employee.user.username, if it's a related field

    # Email subject and content
    email_subject = "Welcome to Tikme Dine!"
    email_body = render_to_string('email_templates/onboarding_email.html', {
        'employee': employee,
        'username': username,  # Pass the username to the template
        'full_link': full_link,
        'image_url': image_url
    })

    # Send email
    email = EmailMessage(
        email_subject,
        email_body,
        settings.DEFAULT_FROM_EMAIL,
        [employee.email]
    )
    email.content_subtype = "html"  # Ensure email is sent as HTML
    email.send()

    return token_record  # Return the token record for tracking


def send_reset_password_email(request, employee, is_reset_notification=False):
    """
    Sends an email with a password reset link to the given employee.
    """
    refresh = RefreshToken.for_user(employee)
    access_token = str(refresh.access_token)

    uid = urlsafe_base64_encode(force_bytes(employee.pk))
    link = reverse('reset_password', kwargs={'uidb64': uid, 'token': access_token})
    full_link = f"https://{request.get_host()}{link}"

    email_subject = "Password Reset Request" if not is_reset_notification else "Password Successfully Reset"
    email_body = f"""
    Dear {employee.first_name},

    Please use the following link to reset your password:
    {full_link}

    Best Regards,
    Tikme Dine Team
    """

    send_mail(email_subject, email_body, 'support@tikmedine.com', [employee.email], fail_silently=False)


def send_account_locked_email(employee):
    """
    Sends an email notification when an account is temporarily locked.
    """
    email_subject = "Account Temporarily Locked"
    email_body = f"""
    Hi {employee.first_name},

    Your account has been temporarily locked due to multiple failed login attempts. Please try again after 24 hours.

    Best Regards,
    Tikme Dine Team
    """
    send_mail(email_subject, email_body, 'support@tikmedine.com', [employee.email], fail_silently=False)


def send_reactivation_confirmation_email(employee):
    """
    Sends an email confirming account reactivation.
    """
    email_subject = "Password Successfully Set for Your Tikme Dine Account"
    email_body = f"""
    Dear {employee.first_name},

    Your account password has been successfully updated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.
    If this wasn't you, contact support immediately.

    Best Regards,
    Tikme Dine Team
    """
    send_mail(email_subject, email_body, 'support@tikmedine.com', [employee.email], fail_silently=False)


def send_permanently_locked_email(employee):
    """
    Sends an email when an account is permanently locked.
    """
    email_subject = "Account Permanently Locked"
    email_body = f"""
    Hi {employee.first_name},

    Your account has been permanently locked due to security reasons. Please contact support for further assistance.

    Best Regards,
    Tikme Dine Team
    """
    send_mail(email_subject, email_body, 'support@tikmedine.com', [employee.email], fail_silently=False)