from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework import status, views
from django.shortcuts import get_object_or_404, render
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.utils.text import slugify
from ..models import *
from ..serializers import *
import jwt, json
import logging

logger = logging.getLogger(__name__)

def validate_token(request):
    """
    Validates the JWT token provided in the request cookies.
    """
    token = request.COOKIES.get('jwt')
    if not token:
        raise AuthenticationFailed('Unauthorized: No token provided.')

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        logger.info(f"✅ Token Decoded: User ID {payload.get('id')}")
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

    is_super_admin = (
        user.role and user.role.role_name == "Super Admin"
    ) or (
        user.job_title and user.job_title.title_name == "Super Admin"
    )

    return is_super_admin


class PermissionListCreateView(views.APIView):
    """
    Handles listing and creating permissions.
    """
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]

    def get(self, request, *args, **kwargs):
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload['id'])

        permissions = Permission.objects.all()
        permission_serializer = PermissionSerializer(permissions, many=True)

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

        return Response(permission_serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        try:
            payload = validate_token(request)
            user = get_object_or_404(User, id=payload["id"])

            if not get_user_permissions(user):
                return Response({"error": "You do not have permission to create permissions."}, status=status.HTTP_403_FORBIDDEN)

            request_data = json.loads(request.body)
            permission_name = request_data.get("name", "").strip()

            if not permission_name:
                return Response({"error": "Permission name cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

            if Permission.objects.filter(name=permission_name).exists():
                return Response({"error": "Permission with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)

            codename = slugify(permission_name)
            content_type = ContentType.objects.get_for_model(JobTitle)

            permission = Permission.objects.create(
                name=permission_name,
                codename=codename,
                content_type=content_type
            )
            
            return Response({"message": "Permission added successfully!", "data": {
                "id": permission.id,
                "name": permission.name,
                "codename": permission.codename,
            }}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PermissionDetailView(views.APIView):
    """
    Handles retrieving, updating, and deleting a single permission.
    """
    renderer_classes = [JSONRenderer]  

    def get(self, request, pk, *args, **kwargs):
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload['id'])

        permission = get_object_or_404(Permission, pk=pk)
        serializer = PermissionSerializer(permission)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload['id'])

        if not get_user_permissions(user):
            raise PermissionDenied("You do not have permission to edit permissions.")

        permission = get_object_or_404(Permission, pk=pk)
        serializer = PermissionSerializer(permission, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, *args, **kwargs):
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload['id'])

        if not get_user_permissions(user):
            raise PermissionDenied("You do not have permission to delete permissions.")

        permission = get_object_or_404(Permission, pk=pk)
        permission.delete()

        return Response({"message": "Permission deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class AssignPermissionToJobTitleView(views.APIView):
    def post(self, request, job_title_id, *args, **kwargs):
        try:
            logger.info(f"📡 Assigning permissions to JobTitle ID: {job_title_id}")

            payload = validate_token(request)
            user = get_object_or_404(User, id=payload['id'])

            if not get_user_permissions(user):
                return Response({"error": "Only Super Admin can assign permissions."}, status=status.HTTP_403_FORBIDDEN)

            job_title = get_object_or_404(JobTitle, id=job_title_id)

            try:
                request_data = json.loads(request.body)
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)

            permission_ids = request_data.get('permission_ids', [])
            if not isinstance(permission_ids, list):
                return Response({"error": "Expected a list of permission IDs."}, status=status.HTTP_400_BAD_REQUEST)

            permissions = Permission.objects.filter(id__in=permission_ids)
            if not permissions.exists():
                return Response({"error": "Invalid permissions provided."}, status=status.HTTP_400_BAD_REQUEST)

            job_title.permissions.add(*permissions)
            return Response(
                {"message": f"Permissions assigned successfully to '{job_title.title_name}'."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"❌ Error assigning permissions: {str(e)}", exc_info=True)
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JobTitleWithPermissionsView(views.APIView):
    """
    API to fetch permissions assigned to a specific job title.
    """
    def get(self, request, job_title_id, *args, **kwargs):
        job_title = get_object_or_404(JobTitle, id=job_title_id)

        # ✅ Ensure permissions exist before returning data
        permissions = job_title.permissions.all()
        
        if not permissions.exists():
            return Response({"message": "No permissions assigned to this job title."}, status=status.HTTP_200_OK)
        
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class JobTitleListView(views.APIView):
    """
    Handles listing all job titles.
    """
    def get(self, request, *args, **kwargs):
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload['id'])

        job_titles = JobTitle.objects.all()
        serializer = JobTitleSerializer(job_titles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class JobTitlePermissionsView(views.APIView):
    """
    API to fetch permissions assigned to a specific job title.
    """
    def get(self, request, job_title_id, *args, **kwargs):
        job_title = get_object_or_404(JobTitle, id=job_title_id)
        permissions = job_title.permissions.all()
        
        if not permissions.exists():
            return Response({"message": "No permissions assigned to this job title."}, status=status.HTTP_200_OK)
        
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RemovePermissionFromJobTitleView(views.APIView):
    """
    API to remove a specific permission from a job title.
    """
    def delete(self, request, job_title_id, permission_id, *args, **kwargs):
        try:
            payload = validate_token(request)
            user = get_object_or_404(User, id=payload['id'])

            if not get_user_permissions(user):
                return Response({"error": "Only Super Admin can remove permissions."}, status=status.HTTP_403_FORBIDDEN)

            job_title = get_object_or_404(JobTitle, id=job_title_id)
            permission = get_object_or_404(Permission, id=permission_id)

            if not job_title.permissions.filter(id=permission_id).exists():
                return Response({"error": "Permission is not assigned to this job title."}, status=status.HTTP_400_BAD_REQUEST)

            job_title.permissions.remove(permission)
            return Response({"message": "Permission removed successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RemoveAllPermissionsFromJobTitleView(views.APIView):
    """
    API to remove all permissions from a job title.
    """

    def delete(self, request, job_title_id, *args, **kwargs):
        try:
            logger.info(f"🗑️ Removing ALL permissions from Job Title ID: {job_title_id}")

            payload = validate_token(request)
            user = get_object_or_404(User, id=payload['id'])

            # ✅ Ensure only Super Admin can remove permissions
            is_super_admin = (
                user.role and user.role.role_name == "Super Admin"
            ) or (
                user.job_title and user.job_title.title_name == "Super Admin"
            )

            if not is_super_admin:
                logger.error("⛔ Unauthorized: Only Super Admin can remove permissions.")
                return Response({"error": "Only Super Admin can remove permissions."}, status=status.HTTP_403_FORBIDDEN)

            job_title = get_object_or_404(JobTitle, id=job_title_id)

            # ✅ Remove all permissions
            job_title.permissions.clear()
            logger.info(f"✅ Successfully removed ALL permissions from '{job_title.title_name}'")

            return Response({"message": "All permissions removed successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"❌ Error removing all permissions: {str(e)}", exc_info=True)
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
