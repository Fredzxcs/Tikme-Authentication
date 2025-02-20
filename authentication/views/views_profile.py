from rest_framework import views
from django.shortcuts import render, get_object_or_404
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from django.http import JsonResponse  # ✅ Correct
from django.core.exceptions import PermissionDenied
from django.conf import settings
from ..models import *
from ..serializers import *
from ..forms import *
import jwt

# Utility Functions
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

def get_user_permissions(user):
    """
    Determines the permissions based on the authenticated user's role.
    """
    if not user.role:
        raise PermissionDenied('Your account does not have an assigned role.')

    if user.role.role_name == 'Super Admin':
        return True
    elif user.role.role_name == 'System Admin':
        return True
    return False

class ProfileView(views.APIView):
    """
    Renders the profile page for the authenticated user.
    """
    def get(self, request):
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload['id'])

        if not user:
            raise PermissionDenied("User not found")

        # Determine the user type for sidebar inclusion
        is_super_admin = user.role.role_name == "Super Admin" if user.role else False
        is_system_admin = user.role.role_name == "System Admin" if user.role else False

        # Render profile template with user data
        return render(request, 'profile.html', {
            'user': user,
            'is_super_admin': is_super_admin,
            'is_system_admin': is_system_admin
        })

class AccountSettingsView(views.APIView):
    """
    Handles the user's account settings and profile update.
    """
    def get(self, request):
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload['id'])

        if not user:
            raise PermissionDenied("User not found")

        # Default values for missing fields
        user_info = {
            'full_name': f"{user.first_name} {user.last_name}",
            'email': user.email or 'Not provided',
            'phone_number': user.phone_number or 'Not provided',
            'profile_picture': user.profile_picture.url if user.profile_picture else '{% static "img/default-profile.jpg" %}'
        }

        form = AccountSettingsForm(instance=user)
        
        is_super_admin = user.role.role_name == "Super Admin" if user.role else False
        is_system_admin = user.role.role_name == "System Admin" if user.role else False
        
        # Pass user info to the template
        return render(request, 'account_settings.html', {
            'form': form,
            'user_info': user_info,
            'is_super_admin': is_super_admin,
            'is_system_admin': is_system_admin
        })

    def patch(self, request):
        try:
            payload = validate_token(request)
            user = get_object_or_404(User, id=payload['id'])

            if not user:
                return JsonResponse({"success": False, "message": "User not found."}, status=404)

            data = request.POST  # ✅ Use request.POST for form data

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
            print(f"ERROR: {e}")  # Debugging
            return JsonResponse({"success": False, "message": str(e)}, status=500)
  
