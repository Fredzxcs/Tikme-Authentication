from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework import status, views
from django.shortcuts import get_object_or_404, render
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from django.conf import settings
from ..models import *
from ..serializers import *
import jwt
import logging

logger = logging.getLogger(__name__)

# Utility Functions
def validate_token(request):
    """
    Validate the JWT token and return the decoded payload.
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
    Determines the users and roles accessible based on the authenticated user's role.
    """
    if not user.role:  # Ensure the user has a role assigned
        raise PermissionDenied('Your account does not have an assigned role.')

    if user.role.role_name == 'Super Admin':
        roles = ['Super Admin', 'System Admin', 'Manager', 'Employee']
        users = User.objects.all()
    elif user.role.role_name == 'System Admin':
        roles = ['Manager', 'Employee']
        users = User.objects.filter(role__role_name__in=roles)
    else:
        raise PermissionDenied('You do not have permission to access this page.')

    return users, roles


# Views
class PermissionListCreateView(views.APIView):
    """
    Handles listing, creating permissions, and rendering the HTML template.
    """
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]  # Order matters here!

    def get(self, request, *args, **kwargs):
        # Validate and authenticate user
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload['id'])

        # Check role-based access
        try:
            get_users_by_role(user)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

        permissions = Permission.objects.all()
        permission_serializer = PermissionSerializer(permissions, many=True)

        # If the request is for HTML, render the template
        if request.accepted_renderer.format == 'html':
            return render(
                request,
                "permissions.html",
                {
                    "permissions": permission_serializer.data,
                    "is_super_admin": user.role.role_name == "Super Admin",
                    "is_system_admin": user.role.role_name == "System Admin",
                },
            )

        # Return JSON response for API requests
        return Response(permission_serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        # Validate and authenticate user
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload['id'])

        # Allow only Super Admins to create permissions
        if user.role.role_name != "Super Admin":
            raise PermissionDenied("You do not have permission to create permissions.")

        serializer = PermissionSerializer(data=request.data)
        if not serializer.is_valid():
            # Include validation errors in the response
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        # Explicitly return JSON response
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class PermissionDetailView(views.APIView):
    """
    Handles retrieving, updating, and deleting a single permission.
    """
    renderer_classes = [JSONRenderer]  # Ensure JSON is used for all methods

    def get(self, request, pk, *args, **kwargs):
        # Validate and authenticate user
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload['id'])

        # Check role-based access
        try:
            get_users_by_role(user)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

        permission = get_object_or_404(Permission, pk=pk)
        serializer = PermissionSerializer(permission)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        # Validate and authenticate user
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload['id'])

        # Allow only Super Admins to edit permissions
        if user.role.role_name != "Super Admin":
            raise PermissionDenied("You do not have permission to edit permissions.")

        permission = get_object_or_404(Permission, pk=pk)
        serializer = PermissionSerializer(permission, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, *args, **kwargs):
        # Validate and authenticate user
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload['id'])

        # Allow only Super Admins to delete permissions
        if user.role.role_name != "Super Admin":
            raise PermissionDenied("You do not have permission to delete permissions.")

        permission = get_object_or_404(Permission, pk=pk)
        permission.delete()

        # Return a JSON response to confirm deletion
        return Response({"message": "Permission deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class AssignPermissionToRoleView(views.APIView):
    """
    Assigns a permission to a role.
    """
    def post(self, request, role_id, *args, **kwargs):
        # Validate and authenticate user
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload['id'])

        # Allow only Super Admins to assign permissions
        if user.role.role_name != "Super Admin":
            raise PermissionDenied("Only Super Admin can assign permissions.")

        role = get_object_or_404(Role, id=role_id)
        permission_id = request.data.get('permission_id')
        permission = get_object_or_404(Permission, id=permission_id)

        role.permissions.add(permission)
        return Response(
            {"message": f"Permission '{permission.name}' assigned to role '{role.role_name}'."},
            status=status.HTTP_200_OK,
        )
    
class RoleWithPermissionsView(views.APIView):
    """
    View to fetch roles and their associated permissions.
    """
    def get(self, request, *args, **kwargs):
        # Validate and authenticate user
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload['id'])

        # Allow only authorized users
        try:
            get_users_by_role(user)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

        roles = Role.objects.prefetch_related('permissions').all()
        data = [
            {
                "role_name": role.role_name,
                "permissions": [permission.name for permission in role.permissions.all()]
            }
            for role in roles
        ]
        return Response(data, status=status.HTTP_200_OK)


class RoleListView(views.APIView):
    """
    Handles listing all roles.
    """
    def get(self, request, *args, **kwargs):
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload['id'])

        # Check role-based access
        try:
            get_users_by_role(user)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
