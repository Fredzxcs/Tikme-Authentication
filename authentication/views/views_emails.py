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


class SendOnboardingEmailView(views.APIView):
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        send_onboarding_email(request, user)
        return JsonResponse({'success': 'Onboarding email sent successfully.'})

class SendLockedEmailView(views.APIView):
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        send_locked_email(user)
        return JsonResponse({'success': 'Locked email sent successfully.'})

class SendReactivationEmailView(views.APIView):
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        send_reactivation_email(user)
        return JsonResponse({'success': 'Reactivation email sent successfully.'})
