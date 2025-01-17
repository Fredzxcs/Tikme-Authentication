from ..emails import *
from ..forms import *
from django.shortcuts import get_object_or_404
from rest_framework import views
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

class TechSupportView(views.APIView):
    def get(self, request):
        form = TechSupportForm()
        return render(request, "tech_support.html", {"form": form})

    def post(self, request):
        form = TechSupportForm(request.POST, request.FILES)
        if form.is_valid():
            # Collect form data
            full_name = form.cleaned_data.get("full_name")
            email = form.cleaned_data.get("email", "no-reply@example.com")
            phone = form.cleaned_data.get("phone", "Not provided")
            description = form.cleaned_data.get("description")

            # Fix: Handle files manually for attachments[]
            attachments = request.FILES.getlist("attachments[]")

            print("FILES LIST:", attachments)  # Debugging

            try:
                # Send email with attachments
                send_tech_support_email(
                    user_full_name=full_name,
                    user_email=email,
                    phone=phone,
                    description=description,
                    attachments=attachments,
                )
                return JsonResponse(
                    {"success": "Your tech support request has been sent successfully!"}
                )
            except Exception as e:
                return JsonResponse(
                    {"error": f"Failed to send tech support email: {str(e)}"},
                    status=500,
                )
        return JsonResponse({"error": form.errors}, status=400)


class ForgotPasswordView(views.APIView):
    """
    Handles Forgot Password functionality.
    """
    def get(self, request):
        return render(request, "forgot_password.html")

    def post(self, request):
        email = request.data.get("email")

        # Check if email is provided
        if not email:
            return JsonResponse({"error": "Email is required."}, status=400)

        # Retrieve the user associated with the email
        user = User.objects.filter(email=email).first()

        if not user:
            logger.warning(f"Forgot password attempted with unregistered email: {email}")
            return JsonResponse({"error": "No account associated with this email."}, status=404)

        # Generate a password reset token and encoded user ID
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Generate a password reset link
        reset_link = f"http://example.com/reset_password/{uid}/{token}/"

        try:
            # Send the reset password email
            send_forgot_password_email(user.name, email, reset_link)
            logger.info(f"Password reset email sent to {email}.")
            return JsonResponse({"success": "A reset link has been sent to your email."})
        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")
            return JsonResponse({"error": "Failed to send email. Please try again later."}, status=500)

class SendOnboardingEmailView(views.APIView):
    def get(self, request, employee_id):
        employee = get_object_or_404(User, pk=employee_id)
        send_onboarding_email(request, employee)
        return JsonResponse({'success': 'Onboarding email sent successfully.'})

class SendLockedEmailView(views.APIView):
    def get(self, request, employee_id):
        employee = get_object_or_404(User, pk=employee_id)
        send_locked_email(employee)
        return JsonResponse({'success': 'Locked email sent successfully.'})

class SendReactivationEmailView(views.APIView):
    def get(self, request, employee_id):
        employee = get_object_or_404(User, pk=employee_id)
        send_reactivation_email(employee)
        return JsonResponse({'success': 'Reactivation email sent successfully.'})