from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.timezone import now
from .models import *
import logging

logger = logging.getLogger(__name__)


def send_tech_support_email(user_full_name, user_email, phone, description, attachments):
    try:
        # Render email content
        html_content = render_to_string("emails/tech_supp_email.html", {
            "user_full_name": user_full_name,
            "user_email": user_email,
            "user_phone": phone,
            "description": description,
            "attachments": attachments,  # Pass attachments for display
        })


        email = EmailMultiAlternatives(
            subject=f"Tech Support Request from {user_full_name or 'Anonymous'}",
            body=f"Tech support request from {user_full_name or 'Anonymous'}.",
            from_email=settings.EMAIL_HOST_USER,
            to=[settings.TECH_SUPPORT_EMAIL],
        )
        
        # Attach files to the email
        for attachment in attachments:
            attachment.seek(0)  # Ensure the file cursor is at the start
            email.attach(attachment.name, attachment.read(), attachment.content_type)

        email.attach_alternative(html_content, "text/html")
        email.send()
    except Exception as e:
        # Log the exception (or handle as needed)
        print(f"Failed to send email: {e}")
        raise e  # Optionally, re-raise the exception if needed

def send_forgot_password_email(user_name, email, reset_link):
    logger.info(f"Preparing to send email to {email} with reset link: {reset_link}")
    try:
        subject = "Reset Your Password"
        body = render_to_string("emails/forgot_email.html", {
            "username": user_name,
            "full_link": reset_link,
        })

        email = EmailMessage(
            subject=subject,
            body=body,
            to=[email],
        )
        email.content_subtype = "html"  # Set email type to HTML
        email.send()
        logger.info(f"Email successfully sent to {email}")
    except Exception as e:
        logger.error(f"Error sending email to {email}: {str(e)}")
        raise e

def send_temp_locked_email(employee):
    """
    Sends an email notification for temporary account lock.
    """
    try:
        subject = "Your Tikme Dine Account is Temporarily Locked"
        body = render_to_string("emails/temp_locked_email.html", {
            "username": employee.get_full_name() or employee.email,
            "unlock_time": employee.locked_until,
            "year": now().year,
        })
        email_message = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[employee.email],
        )
        email_message.content_subtype = "html"
        email_message.send()
        logger.info(f"Temporary lock email sent to {employee.email}")
    except Exception as e:
        logger.error(f"Error sending temporary lock email: {str(e)}")
        raise e


def send_permanent_locked_email(employee):
    """
    Sends an email notification for permanent account lock.
    """
    try:
        subject = "Your Tikme Dine Account is Permanently Locked"
        body = render_to_string("emails/permanent_locked_email.html", {
            "username": employee.get_full_name() or employee.email,
            "year": now().year,
        })
        email_message = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[employee.email],
        )
        email_message.content_subtype = "html"
        email_message.send()
        logger.info(f"Permanent lock email sent to {employee.email}")
    except Exception as e:
        logger.error(f"Error sending permanent lock email: {str(e)}")
        raise e


def send_onboarding_email(request, employee):
    """
    Sends an onboarding email with account setup instructions.
    """
    try:
        # Generate a token and account setup link
        refresh = RefreshToken.for_user(employee)
        access_token = str(refresh.access_token)
        uid = urlsafe_base64_encode(force_bytes(employee.pk))
        link = reverse('setup_account', kwargs={'uidb64': uid, 'token': access_token})
        full_link = request.build_absolute_uri(link)

        # Get the logo URL
        image_url = request.build_absolute_uri(staticfiles_storage.url('images/tikme-logo.png'))

        # Prepare email content
        email_subject = "Welcome to Tikme Dine!"
        username = employee.get_full_name() if employee.get_full_name() else employee.email
        email_body = render_to_string('emails/onboarding_email.html', {
            'employee': employee,
            'username': username,
            'full_link': full_link,
            'image_url': image_url,
            'year': now().year,
        })

        # Send email
        email = EmailMessage(
            subject=email_subject,
            body=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[employee.email]
        )
        email.content_subtype = "html"
        email.send()
    except Exception as e:
        print(f"Error sending onboarding email: {str(e)}")


def send_locked_email(employee):
    """
    Sends an email notification when an account is locked.
    """
    try:
        # Prepare email content
        email_subject = "Your Tikme Dine Account is Locked"
        username = employee.get_full_name() if employee.get_full_name() else employee.email
        email_body = render_to_string('emails/locked_email.html', {
            'username': username,
            'year': now().year,
        })

        # Send email
        email = EmailMessage(
            subject=email_subject,
            body=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[employee.email]
        )
        email.content_subtype = "html"
        email.send()
    except Exception as e:
        print(f"Error sending locked email: {str(e)}")


def send_reactivation_email(employee):
    """
    Sends an account reactivation email.
    """
    try:
        # Prepare email content
        login_link = settings.LOGIN_URL or 'https://example.com/login'  # Fallback login URL
        email_subject = "Your Tikme Dine Account Has Been Reactivated"
        username = employee.get_full_name() if employee.get_full_name() else employee.email
        email_body = render_to_string('emails/reactivation_email.html', {
            'username': username,
            'login_link': login_link,
            'year': now().year,
        })

        # Send email
        email = EmailMessage(
            subject=email_subject,
            body=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[employee.email]
        )
        email.content_subtype = "html"
        email.send()
    except Exception as e:
        print(f"Error sending reactivation email: {str(e)}")