from rest_framework.response import Response
from rest_framework import status, views
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.utils.timezone import now
from django.core.cache import cache
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from ..models import *
from ..serializers import *
from ..emails import *
import jwt
import logging

logger = logging.getLogger(__name__)

# Utility Functions
def validate_token(request):
    """
    Validates the JWT token provided in the request cookies.
    """
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


def get_users_by_role(user):
    """
    Retrieves users and roles based on the current user's role.
    """
    if user.role.role_name == 'Super Admin':
        roles = ['System Admin', 'Manager', 'User']
        users = User.objects.all()
    elif user.role.role_name == 'System Admin':
        roles = ['Manager', 'User']
        users = User.objects.filter(role__role_name__in=roles)
    else:
        raise PermissionDenied('You do not have permission to access this page.')

    return users, roles

class ManageUsersView(views.APIView):
    """
    Handles fetching user, role, and module data for the Manage Users page.
    """

    def get(self, request):
        try:
            # ✅ Validate the user's token
            payload = validate_token(request)
            current_user = get_object_or_404(User, id=payload['id'])

            # ✅ Ensure user has a valid role
            if not current_user.role or not hasattr(current_user.role, 'role_name'):
                logger.warning(f"User {current_user.email} does not have an assigned role.")
                return Response(
                    {'error': 'Your account does not have an assigned role. Please contact the administrator.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # ✅ Automatically unlock temporarily locked users if lock duration expired
            for user in User.objects.filter(status__status_name="Temporarily Locked"):
                locked_until = cache.get(f"locked_until_{user.id}")
                if locked_until and now() >= locked_until:
                    user.status = Status.objects.get_or_create(status_name="Active")[0]
                    user.save()
                    cache.delete(f"locked_until_{user.id}")  # Remove lock

            # ✅ Determine user permissions
            is_super_admin = current_user.role.role_name == "Super Admin"
            is_system_admin = current_user.role.role_name == "System Admin"

            # ✅ Fetch users, roles, and modules based on access level
            users, roles = get_users_by_role(current_user)
            users_data = UserSerializer(users, many=True).data
            roles_data = RoleSerializer(Role.objects.filter(role_name__in=roles), many=True).data
            modules_data = ModuleSerializer(Module.objects.all(), many=True).data

            # ✅ Check request type (HTML or JSON)
            if request.META.get('HTTP_ACCEPT', '').startswith('text/html'):
                return render(
                    request,
                    'manage_users.html',
                    {
                        'users': users_data,
                        'roles': roles_data,
                        'modules': modules_data,
                        'is_super_admin': is_super_admin,
                        'is_system_admin': is_system_admin,
                    },
                )

            return Response(
                {
                    'users': users_data,
                    'roles': roles_data,
                    'modules': modules_data,
                    'is_super_admin': is_super_admin,
                    'is_system_admin': is_system_admin,
                },
                status=status.HTTP_200_OK,
            )

        except PermissionDenied as e:
            logger.error(f"Permission denied: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.exception(f"An error occurred in ManageUsersView: {str(e)}")
            return Response({'error': 'An error occurred while fetching data.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AddUserView(views.APIView):
    def post(self, request):
        try:
            payload = validate_token(request)
            current_user = get_object_or_404(User, id=payload['id'])

            # Permissions check for System Admin
            if current_user.role.role_name == 'System Admin' and request.data.get('role') not in ['Manager', 'User']:
                return Response({'error': 'System Admin can only add Manager or User roles.'}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch related objects by name
            role_name = request.data.get('role', '').strip()
            role = Role.objects.filter(role_name__iexact=role_name).first()
            if not role:
                return Response({'error': f'Role "{role_name}" does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

            module_name = request.data.get('module', '').strip()
            module = Module.objects.filter(module_name__iexact=module_name).first() if module_name else None
            if module_name and not module:
                return Response({'error': f'Module "{module_name}" does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

            job_title_name = request.data.get('job_title', '').strip()
            job_title = JobTitle.objects.filter(title_name__iexact=job_title_name).first() if job_title_name else None
            if job_title_name and not job_title:
                return Response({'error': f'Job title "{job_title_name}" does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

            # Default status
            status_obj = Status.objects.get_or_create(status_name='Pending')[0]

            # Create user
            data = {
                "user_number": request.data.get("user_number"),
                "first_name": request.data.get("first_name"),
                "last_name": request.data.get("last_name"),
                "email": request.data.get("email"),
                "role": role.role_name,
                "module": module.module_name if module else None,
                "job_title": job_title.title_name if job_title else None,
                "status": status_obj.status_name,
            }
            serializer = UserSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except serializers.ValidationError as e:
            return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class EditUserView(views.APIView):
    """
    Handles editing an existing user.
    """

    def get(self, request, pk):
        """
        Retrieves user details for editing.
        """
        try:
            user = get_object_or_404(User, pk=pk)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            payload = validate_token(request)
            user = get_object_or_404(User, id=pk)

            # Store old values
            old_user_number = user.user_number
            old_email = user.email

            # Get new values from request
            new_user_number = request.data.get("user_number", old_user_number)
            new_email = request.data.get("email", old_email)

            # Only validate user_number if changed
            if new_user_number and new_user_number != old_user_number:
                if User.objects.filter(user_number=new_user_number).exclude(id=pk).exists():
                    return Response(
                        {"error": "A user number already exists."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                user.user_number = new_user_number  # Update if changed

            # Only validate email if changed
            if new_email and new_email != old_email:
                if User.objects.filter(email=new_email).exclude(id=pk).exists():
                    return Response(
                        {"error": "A user with this email already exists."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Update email with verification
                user.pending_email = new_email
                user.save()
                send_email_verification(user, request)
                send_email_change_notification(user, old_email)

                return Response(
                    {"message": "A verification email has been sent to your new email. Please confirm the change."},
                    status=status.HTTP_200_OK,
                )

            # Exclude email and user_number from updates if unchanged
            request_data = request.data.copy()
            request_data.pop("user_number", None)
            request_data.pop("email", None)

            # Save other updates
            serializer = UserSerializer(user, data=request_data, partial=True)
            serializer.is_valid(raise_exception=True)
            updated_user = serializer.save()

            return Response(UserSerializer(updated_user).data, status=status.HTTP_200_OK)

        except serializers.ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class DeleteUserView(views.APIView):
    """
    Handles deleting a user.
    """
    def delete(self, request, pk):
        payload = validate_token(request)
        current_user = get_object_or_404(User, id=payload['id'])

        # Fetch the user to be deleted
        target_user = get_object_or_404(User, pk=pk)

        # Check permissions
        if current_user.role.role_name != 'Super Admin':
            raise PermissionDenied('Only Super Admin can delete users.')

        # Prevent Super Admins from deleting themselves
        if current_user == target_user:
            return Response({'error': 'You cannot delete yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        # Delete the target user
        target_user.delete()
        return Response({'message': 'User deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

class StatusActionsView(views.APIView):
    """
    Handles updating user statuses, including activation, suspension, and lock management.
    """

    def post(self, request, pk):
        payload = validate_token(request)
        current_user = get_object_or_404(User, id=payload['id'])
        target_user = get_object_or_404(User, pk=pk)

        # ✅ Only Super Admins can change statuses
        if current_user.role.role_name != 'Super Admin':
            raise PermissionDenied('Only Super Admin can change user statuses.')

        new_status = request.data.get('status', '').capitalize()
        if not new_status or new_status not in ['Pending', 'Active', 'Inactive', 'Suspended', 'Temporarily Locked', 'Permanently Locked']:
            return Response({'error': 'Invalid status provided.'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Handle automatic unlock for temporarily locked users
        if target_user.status.status_name == "Temporarily Locked":
            locked_until = cache.get(f"locked_until_{target_user.id}")
            if locked_until and now() >= locked_until:
                target_user.status = Status.objects.get_or_create(status_name="Active")[0]
                cache.delete(f"locked_until_{target_user.id}")  # Remove lock
                target_user.save()
                return Response({'message': 'User unlocked from temporary lock and set to Active.'}, status=status.HTTP_200_OK)

        # ✅ Handle valid status transitions
        valid_transitions = {
            "Pending": ["Active"],
            "Active": ["Inactive", "Suspended", "Temporarily Locked"],
            "Inactive": ["Active"],
            "Suspended": ["Active"],
            "Temporarily Locked": ["Active"],  # Admin can manually unlock if needed
            "Permanently Locked": ["Active"],  # Admin can manually unlock if needed
        }

        current_status = target_user.status.status_name
        if new_status not in valid_transitions.get(current_status, []):
            return Response({'error': 'Invalid status transition.'}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Update status
        target_user.status = Status.objects.get_or_create(status_name=new_status)[0]
        target_user.save()

        # ✅ Send appropriate email notifications
        if new_status == "Temporarily Locked":
            locked_until_time = now() + timedelta(minutes=15)  # Lock duration: 15 minutes
            cache.set(f"locked_until_{target_user.id}", locked_until_time, timeout=900)
            send_temp_locked_email(target_user)
        elif new_status == "Permanently Locked":
            send_permanent_locked_email(target_user)
        elif new_status == "Active":
            send_reactivation_email(target_user)

        return Response({'message': f'User status updated to {new_status}.'}, status=status.HTTP_200_OK)


class EmailActionsView(views.APIView):
    """
    Handles sending email actions based on user status and permissions.
    """
    def post(self, request, pk):
        payload = validate_token(request)
        current_user = get_object_or_404(User, id=payload['id'])

        # Get target user
        target_user = get_object_or_404(User, pk=pk)

        # Validate permissions
        if current_user.role.role_name not in ['Super Admin', 'System Admin']:
            return Response({'error': 'You do not have permission to send emails.'}, status=status.HTTP_403_FORBIDDEN)

        # Validate email type
        email_type = request.data.get('email_type', '').lower()
        if email_type not in ['onboarding', 'locked', 'reactivation']:
            return Response({'error': 'Invalid email type.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if email_type == "onboarding" and target_user.status.status_name == "Pending":
                send_onboarding_email(request, target_user)
                message = f"Onboarding email sent to {target_user.email}."
            elif email_type == "locked" and target_user.status.status_name == "Inactive":
                send_locked_email(target_user)
                message = f"Locked email sent to {target_user.email}."
            elif email_type == "reactivation" and target_user.status.status_name == "Suspended":
                send_reactivation_email(target_user)
                message = f"Reactivation email sent to {target_user.email}."
            else:
                return Response({'error': 'Invalid email action for the user\'s status.'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'message': message}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyEmailView(views.APIView):
    """
    Handles verification of new email addresses.
    """

    def get(self, request, token):
        try:
            user = get_object_or_404(User, email_verification_token=token)

            # Update email only if the token is valid
            if user.pending_email:
                user.email = user.pending_email
                user.pending_email = None
                user.email_verification_token = None
                user.save()

                return Response(
                    {"message": "Your email has been successfully updated."},
                    status=status.HTTP_200_OK,
                )

            return Response({"error": "Invalid or expired verification token."}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
