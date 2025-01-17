from rest_framework import views
from django.conf import settings
from django.shortcuts import render
from ..models import User
import jwt, logging

logger = logging.getLogger(__name__)

# System Admin Dashboard View
class SystemAdminDashboardView(views.APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            logger.warning("Unauthorized access attempt without token.")
            return render(request, 'admin_login.html', {'error': 'Unauthorized access. Please log in.'}, status=401)

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            logger.info(f"Decoded JWT Payload: {payload}")
        except jwt.ExpiredSignatureError:
            logger.error("JWT token expired.")
            return render(request, 'admin_login.html', {'error': 'Session expired, please log in again.'}, status=401)
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid JWT token: {e}")
            return render(request, 'admin_login.html', {'error': 'Invalid token, please log in again.'}, status=401)

        user_id = payload.get('id')
        if not user_id:
            logger.error("JWT payload does not contain 'id'.")
            return render(request, 'admin_login.html', {'error': 'Invalid token, please log in again.'}, status=401)

        user = User.objects.filter(id=user_id).first()
        if not user:
            logger.error("User not found for the given JWT payload.")
            return render(request, 'admin_login.html', {'error': 'User not found.'}, status=401)

        is_super_admin = user.is_superuser or (user.role and user.role.role_name == "Super Admin")
        is_system_admin = user.role and user.role.role_name == "System Admin"

        if not (is_super_admin or is_system_admin):
            logger.warning(f"Unauthorized access attempt by user {user.employee_number} with role {user.role.role_name if user.role else 'No Role'}.")
            return render(request, 'unauthorized_access.html')

        logger.info(f"Authenticated user: {user.employee_number} with role {user.role.role_name if user.role else 'No Role'}. Accessing System Admin Dashboard.")
        logger.info(f"Is Super Admin: {is_super_admin}")
        logger.info(f"Is System Admin: {is_system_admin}")

        return render(request, 'system_admin_dashboard.html', {
            'user': user,
            'is_super_admin': is_super_admin,
            'is_system_admin': is_system_admin,
        })

