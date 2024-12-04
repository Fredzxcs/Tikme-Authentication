import logging
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

from ..models import Employee
from ..forms import SetupSecurityQuestionsForm, SetupPasswordForm
from ..serializers import SetupSecurityQuestionsSerializer, SetupPasswordSerializer
from ..utils import jwt_authenticate


logger = logging.getLogger(__name__)


def generate_uidb64(user):
    return urlsafe_base64_encode(force_bytes(user.pk))

@api_view(['GET', 'POST'])
def setup_account(request, uidb64, token):
    """
    View to handle account setup using a JWT and user ID.
    """
    try:
        # Validate and decode the token
        access_token = AccessToken(token)
        user_id_from_token = access_token['user_id']  # Assumes token payload includes 'user_id'

        # Decode the UID and retrieve the employee
        uid = force_str(urlsafe_base64_decode(uidb64))
        employee = get_object_or_404(Employee, pk=uid)

        # Ensure the token user matches the employee
        if str(employee.pk) != str(user_id_from_token):
            logger.error("Token does not match the user.")
            return HttpResponse("Token does not match the user.", status=400)

    except (TokenError, ValueError, OverflowError, Employee.DoesNotExist):
        logger.error("Invalid or expired token.")
        return HttpResponse("Invalid or expired token.", status=401)

    # Render the security questions form
    form = SetupSecurityQuestionsForm()
    return render(request, 'setup_security_questions.html', {
        'form': form,
        'employee': employee,
        'token': token,
        'uidb64': uidb64,
    })


@api_view(['POST'])
def setup_security_questions(request):
    """
    API view for submitting the security questions form.
    """
    logger.debug("Attempting to authenticate user...")
    user = jwt_authenticate(request)
    if not user:
        logger.error("Authentication failed. Token missing or invalid.")
        return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

    logger.debug(f"Authenticated user: {user}")

    serializer = SetupSecurityQuestionsSerializer(data=request.data)
    if serializer.is_valid():
        try:
            serializer.save(user=user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = str(AccessToken.for_user(user))
            return Response({
                "message": "Security questions set up successfully.",
                "redirect_url": reverse('setup_password', kwargs={'uidb64': uidb64, 'token': token}),
                "security_answers": request.data.get('security_answers')  # Add security answers to the response
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error saving security questions: {e}")
            return Response({"detail": f"Error: {e}"}, status=status.HTTP_400_BAD_REQUEST)

    logger.debug(f"Validation errors: {serializer.errors}")
    return Response({"detail": "Invalid data submitted.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def setup_password(request, uidb64, token):
    """
    View for setting a new password.
    """
    try:
        # Decode the UID and get the employee   
        uid = force_str(urlsafe_base64_decode(uidb64))
        employee = get_object_or_404(Employee, pk=uid)
        AccessToken(token)  # Validate the token
    except (TypeError, ValueError, OverflowError, Employee.DoesNotExist, TokenError) as e:
        logger.error(f"Error with token or user ID: {e}")
        return render(request, 'setup_password.html', {
            'error_message': "Invalid link or expired token.",
            'uidb64': uidb64,
            'token': token,
        })

    if request.method == 'POST':
        serializer = SetupPasswordSerializer(data=request.POST)  # Use request.POST here
        
        if serializer.is_valid():
            # Save the new password to the employee instance
            serializer.save(employee=employee)
            logger.info("Password set successfully.")
            return render(request, 'setup_password.html', {
                'success_message': "Password set successfully! You can now log in.",
                'uidb64': uidb64,
                'token': token,
            })

        # Handle form validation errors
        return render(request, 'setup_password.html', {
            'form': serializer.errors,  # Display the form with errors
            'error_message': "Invalid data submitted. Please correct the errors.",
            'uidb64': uidb64,
            'token': token,
        })

    # Render the password setup form for GET requests
    serializer = SetupPasswordSerializer()  # Blank form on GET request
    return render(request, 'setup_password.html', {
        'form': serializer.data,
        'uidb64': uidb64,
        'token': token,
    })