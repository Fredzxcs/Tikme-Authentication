from ..emails import send_tech_support_email
from rest_framework import views
from django.http import JsonResponse
from django.shortcuts import render
from ..forms import TechSupportForm


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