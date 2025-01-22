from rest_framework.response import Response
from rest_framework import status, views
from django.shortcuts import get_object_or_404, render
from django.utils.http import urlsafe_base64_decode
from django.core.cache import cache
from rest_framework_simplejwt.tokens import AccessToken, TokenError, RefreshToken
from ..models import User, SecurityQuestion, SecurityAnswer
from ..serializers import SecurityQuestionSerializer, SecurityAnswerSerializer, SetupPasswordSerializer
import logging

logger = logging.getLogger(__name__)

# Helper Functions for Temporary Storage
def save_temp_questions(uid, questions):
    cache.set(f"temp_questions_{uid}", questions, timeout=86400)  # Store for 24 hours

def get_temp_questions(uid):
    return cache.get(f"temp_questions_{uid}")

def clear_temp_questions(uid):
    cache.delete(f"temp_questions_{uid}")

# Setup Account View
class SetupAccountView(views.APIView):
    """
    Handles account setup: security questions and answers.
    """

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(User, pk=uid)

            # Validate Access Token
            try:
                AccessToken(token)  # Validate token
            except TokenError as e:
                logger.warning(f"Access token invalid: {str(e)}")
                if request.META.get('HTTP_ACCEPT', '').startswith('text/html'):
                    return render(request, 'invalid_link.html', status=401)
                return Response({"error": "Invalid or expired token. Please refresh your token."}, status=status.HTTP_401_UNAUTHORIZED)

            # Fetch security questions
            questions = SecurityQuestion.objects.all()
            if not questions.exists():
                return Response({"error": "No security questions available."}, status=status.HTTP_404_NOT_FOUND)

            # Render HTML template if requested
            if request.META.get('HTTP_ACCEPT', '').startswith('text/html'):
                return render(
                    request,
                    'setup_questions.html',
                    {
                        'questions': questions,
                        'uidb64': uidb64,
                        'token': token
                    }
                )

            serializer = SecurityQuestionSerializer(questions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f"Error in SetupAccountView GET: {str(e)}")
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(User, pk=uid)

            # Validate Access Token
            try:
                AccessToken(token)
            except TokenError as e:
                logger.warning(f"Access token invalid: {str(e)}")
                return Response({"error": "Invalid or expired token. Please refresh your token."}, status=status.HTTP_401_UNAUTHORIZED)

            # Validate and save security answers
            answers_data = request.data.get('answers', [])
            if not answers_data:
                return Response({"error": "No answers provided."}, status=status.HTTP_400_BAD_REQUEST)

            errors = []
            seen_questions = set()
            for answer_data in answers_data:
                question_id = answer_data.get('question')
                if not question_id or question_id in seen_questions:
                    errors.append({'question': 'This field is required or duplicate.'})
                    continue
                seen_questions.add(question_id)

                answer_text = answer_data.get('answer')
                question = get_object_or_404(SecurityQuestion, id=question_id)

                # Prevent duplicate entries with update_or_create
                SecurityAnswer.objects.update_or_create(
                    user=user,
                    question=question,
                    defaults={'answer': answer_text}
                )

            if errors:
                return Response({"message": "Partial success.", "errors": errors}, status=status.HTTP_400_BAD_REQUEST)

            # Clear temporary storage and return success
            clear_temp_questions(uid)
            return Response({"message": "Security questions saved successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f"Error in SetupAccountView POST: {str(e)}")
            return Response({"error": "An error occurred while saving your answers."}, status=status.HTTP_400_BAD_REQUEST)


# Refresh Token View
class RefreshTokenView(views.APIView):
    """
    API view to handle refresh tokens.
    """

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            return Response({"access_token": new_access_token}, status=status.HTTP_200_OK)
        except TokenError as e:
            logger.exception(f"Error refreshing token: {str(e)}")
            return Response({"error": "Invalid or expired refresh token."}, status=status.HTTP_400_BAD_REQUEST)


# Setup Password View
class SetupPasswordView(views.APIView):
    """
    Handles password setup for a user.
    """

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(User, pk=uid)

            # Validate Access Token
            try:
                AccessToken(token)
            except TokenError as e:
                logger.warning(f"Access token invalid: {str(e)}")
                if request.META.get('HTTP_ACCEPT', '').startswith('text/html'):
                    return render(request, 'invalid_link.html', status=401)
                return Response({"error": "Invalid or expired token. Please refresh your token."}, status=status.HTTP_401_UNAUTHORIZED)

            # Render HTML template if requested
            if request.META.get('HTTP_ACCEPT', '').startswith('text/html'):
                return render(
                    request,
                    'setup_password.html',
                    {
                        'uidb64': uidb64,
                        'token': token
                    }
                )
            return Response({"message": "Password setup page loaded."}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f"Error in SetupPasswordView GET: {str(e)}")
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(User, pk=uid)
            
            # Validate Access Token
            try:
                AccessToken(token)
            except TokenError as e:
                logger.warning(f"Access token invalid: {str(e)}")
                return Response({"error": "Invalid or expired token."}, status=status.HTTP_401_UNAUTHORIZED)

            serializer = SetupPasswordSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=user)  # Pass the user instance here

                # Update user status to Active
                user.status = "Active"  # Make sure the status field is correct
                user.save()  # Save the updated user object

                return Response({"message": "Password set successfully."}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception(f"Error in SetupPasswordView POST: {str(e)}")
            return Response({"error": "An error occurred while setting your password."}, status=status.HTTP_400_BAD_REQUEST)