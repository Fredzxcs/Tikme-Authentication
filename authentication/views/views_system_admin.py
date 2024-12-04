# Standard Libraries
import logging  # For logging errors

# Django Libraries
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib import messages

# Django REST Framework (DRF)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError


# JWT and Token Management
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

# Custom Imports (Add these according to your application structure)
from ..models import Employee  # Replace with actual Employee model path
from ..forms import EmployeeCreationForm, SetupPasswordForm  # Replace with actual forms
from ..serializers import SetupSecurityQuestionsSerializer  # Replace with actual serializer
from ..emails import send_onboarding_email # Custom utility functions

# Logging Configuration
logger = logging.getLogger(__name__)  # Configure logger if needed


# System Admin Dashboard View
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def system_admin_dashboard(request):
    # Simplify Authentication by using the IsAuthenticated permission
    if not request.user.is_authenticated:
        return redirect('admin_login')  # Redirect if not authenticated
    
    employees = Employee.objects.all()  # List all employees

    if request.method == 'POST':
        # Check for onboarding email action
        if 'send_onboarding_email' in request.POST:
            employee_id = request.POST.get('employee_id')
            employee = get_object_or_404(Employee, id=employee_id)

            # Sending onboarding email logic
            email_sent = send_onboarding_email(employee.email)
            if email_sent:
                messages.success(request, 'Onboarding email sent successfully.')
            else:
                messages.error(request, 'Failed to send onboarding email.')

            return redirect('system_admin_dashboard')  # Avoid form resubmission

        # Handle employee creation or update
        employee_id = request.POST.get('employee_id')
        employee = get_object_or_404(Employee, id=employee_id) if employee_id else None
        form = EmployeeCreationForm(request.POST, instance=employee)
        
        if form.is_valid():
            form.save()
            return redirect('system_admin_dashboard')

    else:
        form = EmployeeCreationForm()

    return render(request, 'system_admin_dashboard.html', {'employees': employees, 'form': form})


# Add Employee View
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_employee(request, employee_id=None):
    # Simplify Authentication by using IsAuthenticated
    if not request.user.is_authenticated:
        return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

    employee = get_object_or_404(Employee, id=employee_id) if employee_id else None
    form = EmployeeCreationForm(request.POST, instance=employee)
    
    if form.is_valid():
        form.save()
        return redirect('system_admin_dashboard')

    return render(request, 'system_admin_dashboard.html', {'form': form, 'employee': employee})


# Change Account Status View
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_status(request, employee_id, status):
    if not request.user.is_authenticated:
        return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

    employee = get_object_or_404(Employee, id=employee_id)
    valid_transitions = {
        'active': ['inactive', 'suspended'],
        'inactive': ['active'],
        'suspended': ['active']
    }

    if status in valid_transitions.get(employee.account_status, []):
        employee.account_status = status
        employee.save()

    return redirect('system_admin_dashboard')


# Reactivate Account View
@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def reactivate_account(request, uidb64, token):
    try:
        # Decode the UID and get the employee
        uid = urlsafe_base64_decode(uidb64).decode()
        employee = get_object_or_404(Employee, pk=uid)
        AccessToken(token)  # Validate the token
    except (TypeError, ValueError, OverflowError, Employee.DoesNotExist, TokenError):
        return render(request, 'invalid_link.html')

    # Handle POST request for password setup
    if request.method == 'POST':
        form = SetupPasswordForm(request.POST)
        if form.is_valid():
            employee.set_password(form.cleaned_data['password'])
            employee.save()
            return redirect('admin_login')
        else:
            logger.error(f"Form errors: {form.errors}")
    
    # GET request, show the password setup form
    form = SetupPasswordForm()
    return render(request, 'reactivate_account.html', {'form': form, 'employee': employee})
