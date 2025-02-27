from rest_framework import views
from django.shortcuts import render, get_object_or_404
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from django.http import JsonResponse
from django.conf import settings
from django.templatetags.static import static
from ..models import User
from ..serializers import UserSerializer
from ..forms import AccountSettingsForm
import jwt

# ✅ Utility Function for Token Validation
def validate_token(request):
    token = request.COOKIES.get('jwt')
    if not token:
        raise AuthenticationFailed('Unauthorized: No token provided.')

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token has expired.')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid token.')

    return payload

class ProfileView(views.APIView):
    def get(self, request):
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload['id'])

        # Ensure the full profile picture URL
        profile_picture_url = request.build_absolute_uri(user.profile_picture.url) if user.profile_picture else static("img/default-profile.jpg")

        user_info = {
            "full_name": f"{user.first_name} {user.last_name}".strip(),
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "user_number": user.user_number or "Not assigned",
            "email": user.email or "Not provided",
            "phone_number": user.phone_number or "Not provided",
            "role": user.role.role_name if user.role else "Not assigned",
            "module": user.module.module_name if user.module else "Not assigned",
            "status": user.status.status_name if user.status else "Active",
            "job_title": user.job_title.title_name if user.job_title else "Not assigned",
            "profile_picture": profile_picture_url,  # ✅ Now using absolute URL
        }

        # ✅ If it's an API request, return JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
            return JsonResponse({"success": True, "user": user_info})

        # ✅ Otherwise, render the profile page
        return render(request, 'profile.html', {
            'user': user_info,
            'is_super_admin': user.role.role_name == "Super Admin" if user.role else False,
            'is_system_admin': user.role.role_name == "System Admin" if user.role else False
        })

# ✅ Profile Detail View - Fetch a Specific User's Profile
class ProfileDetailView(views.APIView):
    """
    Fetches profile details for a specific user based on user_number or id.
    """
    def get(self, request, user_identifier):
        try:
            validate_token(request)

            # Check if the identifier is an ID or user_number
            if user_identifier.isdigit():
                user = get_object_or_404(User, id=int(user_identifier))
            else:
                user = get_object_or_404(User, user_number=user_identifier)

            # Serialize user data
            serializer = UserSerializer(user)
            return JsonResponse({"success": True, "user": serializer.data})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

# ✅ Account Settings View - Fetch & Update Data
class AccountSettingsView(views.APIView):
    """
    Handles retrieving and updating the user's account settings.
    """
    def get(self, request):
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload['id'])

        # Construct user settings data
        user_info = {
            "full_name": f"{user.first_name} {user.last_name}".strip(),
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "email": user.email or "Not provided",
            "phone_number": user.phone_number or "Not provided",
            "profile_picture": user.profile_picture.url if user.profile_picture else static("img/default-profile.jpg"),
        }

        # ✅ If it's an API request, return JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
            return JsonResponse({"success": True, "user": user_info})

        # ✅ Otherwise, render the settings page
        form = AccountSettingsForm(instance=user)
        return render(request, 'account_settings.html', {
            'form': form,
            'user_info': user_info,
            'is_super_admin': user.role.role_name == "Super Admin" if user.role else False,
            'is_system_admin': user.role.role_name == "System Admin" if user.role else False
        })

    def patch(self, request):
        """
        Handles updating user profile details.
        """
        try:
            payload = validate_token(request)
            user = get_object_or_404(User, id=payload['id'])
            data = request.POST

            # ✅ Handle first & last name separately
            if 'full_name' in data:
                name_parts = data['full_name'].strip().split()
                user.first_name = name_parts[0] if len(name_parts) > 0 else ""
                user.last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

            # ✅ Handle phone number update
            if 'phone_number' in data:
                user.phone_number = data['phone_number']

            # ✅ Handle profile picture separately
            if 'profile_picture' in request.FILES:
                user.profile_picture = request.FILES['profile_picture']

            user.save()
            return JsonResponse({"success": True, "message": "Profile updated successfully."})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

# ✅ Account Settings Detail View - Fetch Specific User Settings
class AccountSettingsDetailView(views.APIView):
    """
    Fetches account settings for a specific user based on user_number or id.
    """
    def get(self, request, user_identifier):
        try:
            validate_token(request)

            # Check if the identifier is an ID or user_number
            if user_identifier.isdigit():
                user = get_object_or_404(User, id=int(user_identifier))
            else:
                user = get_object_or_404(User, user_number=user_identifier)

            # Construct response JSON
            user_info = {
                "full_name": f"{user.first_name} {user.last_name}".strip(),
                "first_name": user.first_name or "",
                "last_name": user.last_name or "",
                "email": user.email or "Not provided",
                "phone_number": user.phone_number or "Not provided",
                "profile_picture": user.profile_picture.url if user.profile_picture else static("img/default-profile.jpg"),
            }

            return JsonResponse({"success": True, "user": user_info})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)
