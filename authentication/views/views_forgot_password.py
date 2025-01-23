from datetime import timedelta
from django.utils.timezone import now
from django.core.cache import cache
from django.shortcuts import render, get_object_or_404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import JsonResponse
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from rest_framework import views, status
from rest_framework.response import Response
from ..models import *
from ..emails import *
from ..serializers import *
import json
import logging

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3  # Lock account temporarily after 3 failed attempts
EMAIL_COOLDOWN = 900  # 15 minutes in seconds
TEMPORARY_LOCK_TIME = 900  # 15 minutes in seconds
PERMANENT_LOCK_THRESHOLD = 9  # Lock permanently after 9 total failed attempts


class ForgotPasswordView(views.APIView):
    """
    Handles Forgot Password functionality with 15-minute email cooldown.
    """

    def get(self, request):
        return render(request, "forgot_password.html")

    def post(self, request):
        email = request.data.get("email").strip().lower()  # Convert email to lowercase

        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            logger.warning(f"Forgot password attempted with unregistered email: {email}")
            return Response({"error": "No account associated with this email."}, status=status.HTTP_404_NOT_FOUND)

        # Cache keys
        email_cooldown_key = f"password_reset_cooldown_{user.id}"
        attempts_key = f"forgot_password_attempts_{user.id}"

        # Check cooldown for email requests
        last_request_time = cache.get(email_cooldown_key)
        if last_request_time and now() < last_request_time + timedelta(seconds=EMAIL_COOLDOWN):
            remaining_time = (last_request_time + timedelta(seconds=EMAIL_COOLDOWN)) - now()
            minutes_remaining = remaining_time.seconds // 60
            return Response(
                {"error": f"You must wait {minutes_remaining} minutes before requesting another reset link."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # Generate a reset link for ForgotSetupQuestionsView
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = request.build_absolute_uri(f"/forgot-setup-questions/{uid}/{token}/")

        try:
            # Send forgot password email
            send_forgot_password_email(user.get_full_name(), email, reset_link)
            logger.info(f"Password reset email sent to {email}.")

            # Reset attempts counter and set cooldown
            cache.set(attempts_key, 0, timeout=TEMPORARY_LOCK_TIME)
            cache.set(email_cooldown_key, now(), timeout=EMAIL_COOLDOWN)

            return Response({"success": "A reset link has been sent to your email."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {str(e)}")
            return Response({"error": "Failed to send email. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ForgotSetupQuestionsView(views.APIView):
    """
    Handles verifying answers to security questions during the password reset process.
    """

    def get(self, request, uidb64, token):
        try:
            # Decode user ID
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(User, pk=uid)
            logger.info(f"Fetching security questions for user: {user.email}")

            # Validate the token
            if not default_token_generator.check_token(user, token):
                return JsonResponse({"error": "Invalid or expired token."}, status=400)

            # Fetch the user's security answers and related questions
            security_answers = SecurityAnswer.objects.filter(user=user).select_related("question")[:3]
            if len(security_answers) != 3:
                logger.warning(f"User {user.email} has incomplete security answers.")
                return JsonResponse({"error": "Not enough security questions set."}, status=400)

            # Prepare questions for rendering or JSON response
       
            questions = {}
            for i, answer in enumerate(security_answers):
                questions[f"question_{i+1}"] = answer.question.question_text
                questions[f"question_{i+1}_id"] = answer.question.id

            # If HTML is requested
            if "text/html" in request.META.get("HTTP_ACCEPT", ""):
                return render(request, "forgot_setup_questions.html", {
                    "uidb64": uidb64,
                    "token": token,
                    **questions
                })

            # Otherwise, return JSON
            return JsonResponse(questions, status=200)

        except Exception as e:
            logger.exception(f"Error in ForgotSetupQuestionsView GET: {str(e)}")
            return JsonResponse({"error": "An error occurred while loading security questions."}, status=400)

    def post(self, request, uidb64, token):
        try:
            # Decode user ID from uidb64
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(User, pk=uid)

            # Validate the token
            if not default_token_generator.check_token(user, token):
                return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve security answers from request
            answers_data = request.data.get("answers", [])
            if not answers_data or len(answers_data) != 3:
                return Response({"error": "All questions and answers must be provided."}, status=status.HTTP_400_BAD_REQUEST)

            # Cache key for attempts
            attempts_key = f"forgot_password_attempts_{user.id}"
            attempts = cache.get(attempts_key, 0)

            # Check lock thresholds
            if attempts >= PERMANENT_LOCK_THRESHOLD:
                user.status = Status.objects.get_or_create(status_name="Permanently Locked")[0]
                user.save()
                send_permanent_locked_email(user)
                return Response(
                    {"error": "Your account is permanently locked. Please contact support."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if attempts >= MAX_ATTEMPTS:
                user.status = Status.objects.get_or_create(status_name="Temporarily Locked")[0]
                user.save()
                send_temp_locked_email(user)
                return Response(
                    {"error": "Too many failed attempts. Please try again later."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Validate each answer
            for ans_data in answers_data:
                question_id = ans_data.get("question_id")
                answer_text = ans_data.get("answer", "").strip().lower()

                # Check if the question_id and answer match the stored values
                stored_answer = SecurityAnswer.objects.filter(
                    user=user, question_id=question_id
                ).values_list("answer", flat=True).first()

                if not stored_answer or stored_answer.lower() != answer_text:
                    # Increment attempts on failure
                    cache.set(attempts_key, attempts + 1, timeout=TEMPORARY_LOCK_TIME)
                    logger.warning(
                        f"Answer mismatch for user {user.email}, Question ID: {question_id}, Submitted Answer: {answer_text}"
                    )
                    return Response({"error": "Security answers do not match."}, status=status.HTTP_400_BAD_REQUEST)

            # Reset attempts on success
            cache.set(attempts_key, 0, timeout=TEMPORARY_LOCK_TIME)

            # Redirect to the password reset page
            reset_password_link = f"/reset-password/{uidb64}/{token}/change-password/"
            logger.info(f"Security answers verified for user {user.email}. Redirecting to password reset.")
            return Response({"redirect": reset_password_link}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f"Error in ForgotSetupQuestionsView POST: {str(e)}")
            return Response({"error": "An error occurred while verifying your answers."}, status=status.HTTP_400_BAD_REQUEST)

        
class ForgotSetupPasswordView(views.APIView):
    """
    Handles resetting the password after verifying security questions.
    """

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(User, pk=uid)

            # Validate the token
            if not default_token_generator.check_token(user, token):
                return render(request, 'invalid_link.html', {'token_status': 'invalid'}, status=400)

            return render(
                request,
                "forgot_setup_password.html",
                {"uidb64": uidb64, "token": token},
            )
        except Exception as e:
            logger.exception(f"Error in ForgotSetupPasswordView GET: {str(e)}")
            return render(request, 'invalid_link.html', {'token_status': 'invalid'}, status=400)

    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(User, pk=uid)

            # Validate the token
            if not default_token_generator.check_token(user, token):
                return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

            serializer = SetupPasswordSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=user)  # Update the user's password
                return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Error in ForgotSetupPasswordView POST: {str(e)}")
            return Response({"error": "An error occurred while resetting your password."}, status=status.HTTP_400_BAD_REQUEST)

def validate_password(request):
    if request.method == 'POST':
        try:
            # Parse the request body
            body = json.loads(request.body)
            new_password = body.get('password')
            uidb64 = body.get('uidb64')
            token = body.get('token')

            # Validate that all required fields are provided
            if not new_password or not uidb64 or not token:
                return JsonResponse({"error": "Password, uidb64, and token are required."}, status=400)

            # Decode the UID and fetch the user
            try:
                uid = urlsafe_base64_decode(uidb64).decode()
                user = get_object_or_404(User, pk=uid)
            except (ValueError, User.DoesNotExist):
                return JsonResponse({"error": "Invalid user identifier."}, status=400)

            # Validate the token
            if not default_token_generator.check_token(user, token):
                return JsonResponse({"error": "Invalid or expired token."}, status=400)

            # Check if the password matches the user's current password
            if user.check_password(new_password):
                return JsonResponse({"is_old_password": True}, status=200)

            return JsonResponse({"is_old_password": False}, status=200)

        except json.JSONDecodeError:
            logger.error("Invalid JSON in request body.")
            return JsonResponse({"error": "Invalid JSON."}, status=400)

        except Exception as e:
            logger.error(f"Error validating password: {str(e)}")
            return JsonResponse({"error": "An error occurred while validating the password."}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=400)