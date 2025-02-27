from rest_framework.response import Response
from rest_framework import status, views
from django.shortcuts import render, get_object_or_404
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from django.conf import settings
from ..models import *
from ..serializers import *
import jwt


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
    if not user.role:  # Ensure the user has a role assigned
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


class ModuleListCreateView(views.APIView):
    """
    Handles listing, creating modules, and rendering the HTML template with users and modules context.
    """
    def get(self, request):
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload['id'])

        if not user.role:
            raise PermissionDenied("Your account does not have an assigned role.")

        try:
            users, roles = get_users_by_role(user)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

        modules = Module.objects.all()
        module_serializer = ModuleSerializer(modules, many=True)

        if request.META.get("HTTP_ACCEPT", "").startswith("text/html"):
            return render(
                request,
                "modules.html",
                {
                    "modules": module_serializer.data,
                    "users": users,
                    "is_super_admin": user.role.role_name == "Super Admin",
                    "is_system_admin": user.role.role_name == "System Admin",
                },
            )

        return Response(module_serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload["id"])

        if user.role.role_name != "Super Admin":
            return Response({"error": "You do not have permission to create modules."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ModuleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        module = serializer.save()

        return Response(ModuleSerializer(module).data, status=status.HTTP_201_CREATED)


class ModuleDetailView(views.APIView):
    """
    Handles retrieving, updating, and deleting a single module.
    """
    def get(self, request, pk):
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload["id"])

        module = get_object_or_404(Module, pk=pk)
        serializer = ModuleSerializer(module)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload["id"])

        if user.role.role_name != "Super Admin":
            return Response({"error": "You do not have permission to edit modules."}, status=status.HTTP_403_FORBIDDEN)

        module = get_object_or_404(Module, pk=pk)
        serializer = ModuleSerializer(module, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_module = serializer.save()

        return Response(ModuleSerializer(updated_module).data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload["id"])

        if user.role.role_name != "Super Admin":
            return Response({"error": "You do not have permission to delete modules."}, status=status.HTTP_403_FORBIDDEN)

        module = get_object_or_404(Module, pk=pk)
        module.delete()
        return Response({"message": "Module deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
