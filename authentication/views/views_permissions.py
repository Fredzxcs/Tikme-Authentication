from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework import status, views
from django.shortcuts import get_object_or_404, render
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from django.conf import settings
from ..models import *
from ..serializers import *
import jwt, json
import logging

logger = logging.getLogger(__name__)

# Utility Functions
def validate_token(request):
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

    if user.role.role_name == 'Super Admin':
        return True
    elif user.role.role_name == 'System Admin':
        return True
    return False

class PermissionListCreateView(views.APIView):
    """
    Handles listing, creating permissions, and rendering the HTML template.
    """
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]  

    def get(self, request, *args, **kwargs):
        # Validate and authenticate user
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload['id'])

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
        try:
            payload = validate_token(request)
            user = get_object_or_404(User, id=payload['id'])

            # 🔍 Debug: Log request data
            logger.info(f"Incoming POST request data: {request.data}")

            # 🛠️ Fix: Check if job_title exists before accessing title_name
            if not user.job_title:
                logger.error("❌ User does not have a job title assigned.")
                return Response({"error": "User does not have a job title assigned."}, status=status.HTTP_400_BAD_REQUEST)

            if user.job_title.title_name != "Super Admin":
                logger.error("❌ User does not have permission to create permissions.")
                return Response({"error": "You do not have permission to create permissions."}, status=status.HTTP_403_FORBIDDEN)

            serializer = PermissionSerializer(data=request.data)

            # 🔍 Debug: Check serializer validation
            if not serializer.is_valid():
                logger.error(f"❌ Serializer Errors: {serializer.errors}")
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            logger.info(f"✅ Permission created successfully: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"❌ Error creating permission: {str(e)}")
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

        if user.job_title.title_name != "Super Admin":
            raise PermissionDenied("You do not have permission to edit permissions.")

        permission = get_object_or_404(Permission, pk=pk)
        serializer = PermissionSerializer(permission, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, *args, **kwargs):
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload['id'])

        if user.job_title.title_name != "Super Admin":
            raise PermissionDenied("You do not have permission to delete permissions.")

        permission = get_object_or_404(Permission, pk=pk)
        permission.delete()

        return Response({"message": "Permission deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class AssignPermissionToJobTitleView(views.APIView):
    """
    Assigns permissions to a job title.
    """
    def post(self, request, job_title_id, *args, **kwargs):
        try:
            logger.info(f"📡 Received request to assign permissions to JobTitle ID: {job_title_id}")

            payload = validate_token(request)
            user = get_object_or_404(User, id=payload['id'])

            # 🛠️ Fix: Ensure the user has a job title
            if not user.job_title:
                logger.error("❌ User does not have a job title assigned.")
                return Response(
                    {"error": "User does not have a job title assigned."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if user.job_title.title_name != "Super Admin":
                logger.error("⛔ Unauthorized: Only Super Admin can assign permissions.")
                return Response({"error": "Only Super Admin can assign permissions."}, status=status.HTTP_403_FORBIDDEN)

            job_title = get_object_or_404(JobTitle, id=job_title_id)

            # ✅ Fix: Ensure request body is valid JSON
            try:
                request_data = json.loads(request.body)
            except json.JSONDecodeError:
                logger.error("❌ Invalid JSON format received.")
                return Response({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)

            permission_ids = request_data.get('permission_ids', [])
            if not isinstance(permission_ids, list):  # ✅ Validate type
                logger.error("❌ permission_ids should be a list.")
                return Response({"error": "Expected a list of permission IDs."}, status=status.HTTP_400_BAD_REQUEST)

            if not permission_ids:
                logger.error("⚠️ No permissions provided.")
                return Response({"error": "No permissions provided."}, status=status.HTTP_400_BAD_REQUEST)

            permissions = Permission.objects.filter(id__in=permission_ids)
            if not permissions.exists():
                logger.error(f"❌ Invalid permissions provided: {permission_ids}")
                return Response({"error": "Invalid permissions provided."}, status=status.HTTP_400_BAD_REQUEST)

            job_title.permissions.add(*permissions)  # ✅ Assign multiple permissions
            logger.info(f"✅ Successfully assigned {permissions.count()} permissions to '{job_title.title_name}'")

            return Response(
                {"message": f"Permissions assigned successfully to '{job_title.title_name}'."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"❌ Critical error assigning permissions: {str(e)}", exc_info=True)
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JobTitleWithPermissionsView(views.APIView):
    """
    View to fetch job titles and their associated permissions.
    """
    def get(self, request, *args, **kwargs):
        payload = validate_token(request)
        user = get_object_or_404(User, id=payload['id'])

        job_titles = JobTitle.objects.prefetch_related('permissions').all()
        data = [
            {
                "title_name": job_title.title_name,
                "permissions": [permission.name for permission in job_title.permissions.all()]
            }
            for job_title in job_titles
        ]
        return Response(data, status=status.HTTP_200_OK)


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

        # Ensure JobTitle has a ManyToMany relationship with Permission
        permissions = job_title.permissions.all()
        
        if not permissions.exists():
            return Response({"message": "No permissions found for this job title."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)