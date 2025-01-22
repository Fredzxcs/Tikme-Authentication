from rest_framework.response import Response
from rest_framework import status, views
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
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
        roles = ['System Admin', 'Manager', 'Employee']
        users = User.objects.all()
    elif user.role.role_name == 'System Admin':
        roles = ['Manager', 'Employee']
        users = User.objects.filter(role__role_name__in=roles)
    else:
        raise PermissionDenied('You do not have permission to access this page.')

    return users, roles

class ManageUsersView(views.APIView):
    """
    Handles fetching user, role, and module data for the manage users page.
    """
    def get(self, request):
        try:
            # Validate the user's token
            payload = validate_token(request)
            current_user = get_object_or_404(User, id=payload['id'])

            # Ensure the user has a valid role
            if not current_user.role or not hasattr(current_user.role, 'role_name'):
                logger.warning(f"User {current_user.email} does not have an assigned role.")
                return Response(
                    {'error': 'Your account does not have an assigned role. Please contact the administrator.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Determine if the user is a Super Admin or System Admin
            is_super_admin = current_user.role.role_name == 'Super Admin'
            is_system_admin = current_user.role.role_name == 'System Admin'

            # Fetch users and roles based on the current user's permissions
            users, roles = get_users_by_role(current_user)
            employees_data = UserSerializer(users, many=True).data
            roles_data = RoleSerializer(Role.objects.filter(role_name__in=roles), many=True).data

            # Fetch all modules
            modules_data = ModuleSerializer(Module.objects.all(), many=True).data

            # Check if the request is for HTML or JSON
            if request.META.get('HTTP_ACCEPT', '').startswith('text/html'):
                # Render the HTML template
                return render(
                    request,
                    'manage_users.html',  # Ensure this template exists in your project
                    {
                        'employees': employees_data,
                        'roles': roles_data,
                        'modules': modules_data,
                        'is_super_admin': is_super_admin,
                        'is_system_admin': is_system_admin,
                    },
                )
            
            # Return JSON response for the frontend
            return Response(
                {
                    'employees': employees_data,
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
            if current_user.role.role_name == 'System Admin' and request.data.get('role') not in ['Manager', 'Employee']:
                return Response({'error': 'System Admin can only add Manager or Employee roles.'}, status=status.HTTP_400_BAD_REQUEST)

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
                "employee_number": request.data.get("employee_number"),
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

                # Ensure proper role and module logic
                if 'role' in request.data:
                    if request.data['role'] == "Super Admin" and User.objects.filter(role__role_name="Super Admin").exclude(id=pk).exists():
                        return Response({"error": "Only one Super Admin is allowed."}, status=status.HTTP_400_BAD_REQUEST)

                serializer = UserSerializer(user, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                updated_user = serializer.save()

                return Response(UserSerializer(updated_user).data, status=status.HTTP_200_OK)
            except JobTitle.DoesNotExist:
                return Response({"error": "The provided job title does not exist."}, status=status.HTTP_400_BAD_REQUEST)
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
    Handles updating user statuses: Pending -> Active, Active -> Inactive/Suspended, etc.
    """
    def post(self, request, pk):
        payload = validate_token(request)
        current_user = get_object_or_404(User, id=payload['id'])

        target_user = get_object_or_404(User, pk=pk)

        # Only Super Admin can change user statuses
        if current_user.role.role_name != 'Super Admin':
            raise PermissionDenied('Only Super Admin can change user statuses.')

        new_status = request.data.get('status', '').capitalize()
        if not new_status or new_status not in ['Pending', 'Active', 'Inactive', 'Suspended']:
            return Response({'error': 'Invalid status provided.'}, status=status.HTTP_400_BAD_REQUEST)

        # Handle status transitions
        if target_user.status.status_name == 'Pending' and new_status == 'Active':
            # Automatically activate after setup
            target_user.status = Status.objects.get_or_create(status_name='Active')[0]
        elif target_user.status.status_name == 'Active' and new_status in ['Inactive', 'Suspended']:
            target_user.status = Status.objects.get_or_create(status_name=new_status)[0]
        elif target_user.status.status_name == 'Inactive' and new_status == 'Active':
            target_user.status = Status.objects.get_or_create(status_name='Active')[0]
        elif target_user.status.status_name == 'Suspended' and new_status == 'Active':
            target_user.status = Status.objects.get_or_create(status_name='Active')[0]
        else:
            return Response({'error': 'Invalid status transition.'}, status=status.HTTP_400_BAD_REQUEST)

        target_user.save()
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

