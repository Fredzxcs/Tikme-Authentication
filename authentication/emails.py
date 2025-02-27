from django.urls import reverse
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from .models import User, Status
import logging

logger = logging.getLogger(__name__)


### 🔒 **Temporary Lock Email**
def send_temp_locked_email(user):
    try:
        subject = "🔒 Your Tikme Dine Account is Temporarily Locked"
        body = render_to_string("emails/temp_locked_email.html", {
            "username": user.get_full_name() or user.email,
            "unlock_time": user.temporary_lock_until.strftime('%Y-%m-%d %H:%M:%S') if user.temporary_lock_until else "15 minutes",
            "year": now().year,
        })
        email_message = EmailMessage(subject, body, from_email=settings.DEFAULT_FROM_EMAIL, to=[user.email])
        email_message.content_subtype = "html"
        email_message.send()
        logger.info(f"✅ Temporary lock email sent to {user.email}")
    except Exception as e:
        logger.error(f"❌ Error sending temporary lock email: {str(e)}")
        raise e


### 🚨 **Permanent Lock Email**
def send_permanent_locked_email(user):
    try:
        subject = "🚨 Your Tikme Dine Account is Permanently Locked"
        body = render_to_string("emails/permanent_locked_email.html", {
            "username": user.get_full_name() or user.email,
            "year": now().year,
        })
        email_message = EmailMessage(subject, body, from_email=settings.DEFAULT_FROM_EMAIL, to=[user.email])
        email_message.content_subtype = "html"
        email_message.send()
        logger.info(f"✅ Permanent lock email sent to {user.email}")
    except Exception as e:
        logger.error(f"❌ Error sending permanent lock email: {str(e)}")
        raise e


### 🔄 **Account Reactivation Email**
def send_reactivation_email(user):
    try:
        login_link = settings.LOGIN_URL or 'http://127.0.0.1:8001/admin_login/'
        subject = "✅ Your Tikme Dine Account Has Been Reactivated!"
        body = render_to_string("emails/reactivation_email.html", {
            "username": user.get_full_name() or user.email,
            "login_link": login_link,
            "year": now().year,
        })
        email_message = EmailMessage(subject, body, from_email=settings.DEFAULT_FROM_EMAIL, to=[user.email])
        email_message.content_subtype = "html"
        email_message.send()
        logger.info(f"✅ Reactivation email sent to {user.email}")
    except Exception as e:
        logger.error(f"❌ Error sending reactivation email: {str(e)}")
        raise e


### 🛑 **Account Locked Email (General Lock)**
def send_locked_email(user):
    try:
        subject = "🔒 Your Tikme Dine Account is Locked"
        body = render_to_string("emails/locked_email.html", {
            "username": user.get_full_name() or user.email,
            "year": now().year,
        })
        email_message = EmailMessage(subject, body, from_email=settings.DEFAULT_FROM_EMAIL, to=[user.email])
        email_message.content_subtype = "html"
        email_message.send()
        logger.info(f"✅ Locked email sent to {user.email}")
    except Exception as e:
        logger.error(f"❌ Error sending locked email: {str(e)}")
        raise e


### 📩 **Forgot Password Email**
def send_forgot_password_email(user_name, email, reset_link):
    try:
        subject = "🔑 Reset Your Password"
        body = render_to_string("emails/forgot_email.html", {
            "username": user_name,
            "full_link": reset_link,
        })
        email_message = EmailMessage(subject, body, from_email=settings.DEFAULT_FROM_EMAIL, to=[email])
        email_message.content_subtype = "html"
        email_message.send()
        logger.info(f"✅ Forgot password email sent to {email}")
    except Exception as e:
        logger.error(f"❌ Error sending forgot password email: {str(e)}")
        raise e


### 📢 **Onboarding Email**
def send_onboarding_email(request, user):
    try:
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        link = reverse('setup_account', kwargs={'uidb64': uid, 'token': access_token})
        full_link = request.build_absolute_uri(link)

        email_subject = "🎉 Welcome to Tikme Dine!"
        email_body = render_to_string("emails/onboarding_email.html", {
            "user": user,
            "username": user.get_full_name() or user.email,
            "full_link": full_link,
            "year": now().year,
        })
        email_message = EmailMessage(email_subject, email_body, from_email=settings.DEFAULT_FROM_EMAIL, to=[user.email])
        email_message.content_subtype = "html"
        email_message.send()
        logger.info(f"✅ Onboarding email sent to {user.email}")
    except Exception as e:
        logger.error(f"❌ Error sending onboarding email: {str(e)}")
        raise e


### ✉️ **Email Change Notification**
def send_email_change_notification(user, old_email):
    try:
        subject = "⚠️ Security Alert: Email Change Requested"
        body = render_to_string("emails/email_change_notification.html", {
            "username": user.get_full_name() or user.email,
            "old_email": old_email,
            "new_email": user.pending_email,
            "year": now().year,
        })
        email_message = EmailMessage(subject, body, from_email=settings.DEFAULT_FROM_EMAIL, to=[old_email])
        email_message.content_subtype = "html"
        email_message.send()
        logger.info(f"✅ Email change notification sent to {old_email}")
    except Exception as e:
        logger.error(f"❌ Error sending email change notification: {str(e)}")
        raise e


### ✅ **Email Verification**
def send_email_verification(user, request):
    try:
        verification_token = get_random_string(length=32)
        user.email_verification_token = verification_token
        user.save()

        verification_link = request.build_absolute_uri(reverse("verify-email", kwargs={"token": verification_token}))

        subject = "📩 Verify Your New Email Address"
        body = render_to_string("emails/verification_email.html", {
            "username": user.get_full_name() or user.email,
            "verification_link": verification_link,
            "year": now().year,
        })

        email_message = EmailMessage(subject, body, from_email=settings.DEFAULT_FROM_EMAIL, to=[user.pending_email])
        email_message.content_subtype = "html"
        email_message.send()
        logger.info(f"✅ Verification email sent to {user.pending_email}")
    except Exception as e:
        logger.error(f"❌ Error sending verification email: {str(e)}")
        raise e
