from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from rest_framework import status, views
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from ..models import *
from ..serializers import *
import jwt
from django.conf import settings


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
    Determines the users and roles accessible based on the authenticated user's role.
    """
    if not user.role:
        raise PermissionDenied('Your account does not have an assigned role.')

    if user.role.role_name == 'Super Admin':
        roles = ['Super Admin', 'System Admin', 'Manager', 'User']
        users = User.objects.all()
    elif user.role.role_name == 'System Admin':
        roles = ['Manager', 'User']
        users = User.objects.filter(role__role_name__in=roles)
    else:
        raise PermissionDenied('You do not have permission to access this page.')

    return users, roles


class RoleListCreateView(views.APIView):
    """
    Handles listing, creating roles, and rendering the HTML template with users and roles context.
    """
    def get(self, request):
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload['id'])

        # Ensure the user has a role and is authenticated
        if not user.role:
            raise PermissionDenied('Your account does not have an assigned role.')

        try:
            users, roles = get_users_by_role(user)
        except PermissionDenied as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

        # Fetch roles
        all_roles = Role.objects.all()
        role_serializer = RoleSerializer(all_roles, many=True)

        # If the request is for HTML, render the template
        if request.META.get('HTTP_ACCEPT', '').startswith('text/html'):
            return render(
                request,
                'roles.html',
                {
                    'roles': role_serializer.data,
                    'users': users,
                    'is_super_admin': user.role.role_name == 'Super Admin',
                    'is_system_admin': user.role.role_name == 'System Admin',
                }
            )

        # Return JSON response otherwise
        return Response(role_serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Creates a new role. Only Super Admin and System Admin can create roles.
        """
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload['id'])

        if user.role.role_name not in ['Super Admin', 'System Admin']:
            return Response({'error': 'You do not have permission to create roles.'}, status=status.HTTP_403_FORBIDDEN)

        # Handle role creation
        serializer = RoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = serializer.save()

        return Response(RoleSerializer(role).data, status=status.HTTP_201_CREATED)


class RoleDetailView(views.APIView):
    """
    Handles retrieving, updating, and deleting a single role.
    """
    def get(self, request, pk):
        """
        Retrieves details of a specific role.
        """
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload['id'])

        role = get_object_or_404(Role, pk=pk)
        serializer = RoleSerializer(role)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Updates an existing role. Only Super Admin can update roles.
        """
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload['id'])

        if user.role.role_name != 'Super Admin':
            return Response({'error': 'You do not have permission to edit roles.'}, status=status.HTTP_403_FORBIDDEN)

        role = get_object_or_404(Role, pk=pk)
        serializer = RoleSerializer(role, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_role = serializer.save()

        return Response(RoleSerializer(updated_role).data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """
        Deletes a role. Only Super Admin can delete roles.
        """
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload['id'])

        if user.role.role_name != 'Super Admin':
            return Response({'error': 'You do not have permission to delete roles.'}, status=status.HTTP_403_FORBIDDEN)

        role = get_object_or_404(Role, pk=pk)
        role.delete()
        return Response({'message': 'Role deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
