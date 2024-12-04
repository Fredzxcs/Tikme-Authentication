# Standard Library Imports
import logging
from datetime import datetime, timedelta
import jwt
import json

# Django Core Imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, get_user_model, login
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth.models import Group
from django.urls import reverse

# Django REST Framework Imports
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, authentication_classes

from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status

# Local Imports
from ..models import Employee
from ..forms import EmployeeCreationForm, SetupSecurityQuestionsForm, SetupPasswordForm, TechSupportForm
from ..serializers import SetupSecurityQuestionsSerializer, SetupPasswordSerializer
from authentication.utils import jwt_authenticate 
from ..emails import (  # Add the new email library imports
    send_reset_password_email,
    send_account_locked_email,
    send_permanently_locked_email,
    send_reactivation_confirmation_email,
)


User = get_user_model()
logger = logging.getLogger(__name__)


# Helper function to generate JWT token for the authenticated user
def generate_jwt_token(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username'].strip()
        password = request.POST['password'].strip()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('/systemadmin/')
            elif user.is_system_admin():
                return redirect('/system-admin/dashboard/')
            elif user.is_employee():
                return redirect('/admin/dashboard/')
            else:
                messages.error(request, 'User role is not recognized')
                return redirect('admin_login')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('admin_login')

    return render(request, 'admin_login.html')


# Unauthorized access view
def unauthorized_access(request):
    return render(request, 'unauthorized_access.html')

# invalid or expired token view
def invalid_link(request):
    return render(request, 'invalid_link.html')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        employee = Employee.objects.filter(email=email).first()

        if employee:
            send_reset_password_email(request, employee)
            messages.success(request, "Password reset link sent to your email.")
        else:
            messages.error(request, "Email is not registered.")

        # Redirect back to the same page to display messages and prevent form resubmission
        return redirect('forgot_password')

    return render(request, 'forgot_password.html')


@api_view(['POST'])
def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        employee = get_object_or_404(Employee, pk=uid)
        RefreshToken(token)  # JWT verification
    except Exception:
        employee = None

    if employee and request.method == 'POST':
        password_form = SetupPasswordForm(request.POST)
        if password_form.is_valid():
            employee.set_password(password_form.cleaned_data['password'])
            employee.save()
            return redirect('login')
    else:
        password_form = SetupPasswordForm()

    return render(request, 'reset_password.html', {'password_form': password_form})

# Reactivation of account using JWT for authentication
@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def reactivate_account(request, uidb64, token):
    try:
        # Decode the user ID from the URL
        uid = urlsafe_base64_decode(uidb64).decode()
        employee = Employee.objects.get(pk=uid)  # Get the employee by ID
    except (TypeError, ValueError, OverflowError, Employee.DoesNotExist):
        employee = None

    # Validate the JWT token
    try:
        # Decode the token and validate it
        AccessToken(token)  # This will raise an error if the token is invalid
    except TokenError:
        return render(request, 'invalid_link.html')  # Token is invalid, show error page

    if employee is not None:  # If employee is found
        if request.method == 'POST':
            form = SetupPasswordForm(request.POST)
            if form.is_valid():
                employee.set_password(form.cleaned_data['password'])  # Set new password
                employee.save()  # Save the employee instance
                return redirect('admin_login')  # Redirect to login page
            else:
                logger.error(f"Form errors: {form.errors}")
        else:
            form = SetupPasswordForm()
        
        return render(request, 'reactivate_account.html', {'form': form, 'employee': employee})  # Render reactivation form
    else:
        return render(request, 'invalid_link.html')  # Employee not found, show error page
    []

def tech_support(request):
    if request.method == 'POST':
        form = TechSupportForm(request.POST, request.FILES)
        if form.is_valid():
            # Get form data
            full_name = form.cleaned_data['full_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data.get('phone_number', 'N/A')
            issue_description = form.cleaned_data['issue_description']
            attachment = request.FILES.get('attachment')

            # Send email
            try:
                send_mail(
                    f'Tech Support Request from {full_name}',
                    f'Issue Details:\n\n{issue_description}\n\nPhone: {phone_number}\nEmail: {email}',
                    email,  # Sender's email
                    ['support@tikmedine.com'],  # Receiver's email (e.g., support team)
                    fail_silently=False,
                )
                # On success, render the success page
                return render(request, 'tech_support.html', {'form': form, 'success': True})
            except Exception as e:
                # If sending the email fails, render the error page
                return render(request, 'tech_support.html', {'form': form, 'error': f'Error sending email: {str(e)}'})

        else:
            # If form validation fails, render with validation errors
            return render(request, 'tech_support.html', {'form': form, 'error': 'Form is not valid.'})

    else:
        form = TechSupportForm()
    return render(request, 'tech_support.html', {'form': form})