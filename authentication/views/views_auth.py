from rest_framework.response import Response
from django.http import JsonResponse
from django.conf import settings
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import AuthenticationFailed, NotFound
from rest_framework import status, views
from django.shortcuts import render
from ..models import User
from ..serializers import UserSerializer
import jwt, datetime
import logging

logger = logging.getLogger(__name__)


# Register User View
class RegisterView(views.APIView):
    """
    Handles user registration
    """
    permission_classes = [AllowAny]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if 'password' in serializer.validated_data:
            user.set_password(serializer.validated_data['password'])  # Hash password
            user.save()
        return JsonResponse(serializer.data)


# User Read, Update, Delete View
class RegisterViewRUD(views.APIView):
    """
    Handles retrieve, update, and delete operations for users
    """
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise NotFound(detail="User not found", code=404)

    def put(self, request, pk):
        user = self.get_object(pk)
        serializer = UserSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return JsonResponse(serializer.data)

    def patch(self, request, pk):
        user = self.get_object(pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return JsonResponse(serializer.data)

    def delete(self, request, pk):
        user = self.get_object(pk)
        user.delete()
        return JsonResponse({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# Login View
class LoginView(views.APIView):
    """
    Handles user login and JWT token generation
    """
    def get(self, request):
        return render(request, 'admin_login.html')

    def post(self, request):
        employee_number = request.data.get('employee_number')
        password = request.data.get('password')

        if not employee_number or not password:
            raise AuthenticationFailed('Employee number and password are required!')

        user = User.objects.filter(employee_number=employee_number).first()
        if not user or not user.check_password(password):
            raise AuthenticationFailed('Invalid credentials!')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow(),
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        redirection_url = self.get_redirection_url(user, token)
        logger.info(f"Redirecting user {user.employee_number} to {redirection_url}")

        user_data = {
            'id': user.role.id if user.role else None,
            'user_name': user.name,
            'user': user.employee_number,
            'role_name': user.role.role_name if user.role else None,
            'module': user.module.module_name if user.module else None,
        }

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token,
            'data': user_data,
            'redirect_to': redirection_url,
        }
        return response

    def get_redirection_url(self, user, token):
        if user.is_superuser:
            return '/system_admin_dashboard/'
        elif user.role and user.role.role_name == "System Admin":
            return '/system_admin_dashboard/'
        elif user.module and user.module.module_name == 'Reservations':
            return f"{settings.RESERVATIONS_URL}?token={token}"
        elif user.module and user.module.module_name == 'Logistics':
            return f"{settings.LOGISTICS_URL}?token={token}"
        elif user.module and user.module.module_name == 'Finance':
            return f"{settings.FINANCE_URL}?token={token}"
        return '/unauthorized_access/'



# Landing Page View
class LandingPageView(views.APIView):
    """
    Renders the landing page
    """
    def get(self, request):
        return render(request, 'admin_login.html')


class SystemAdminDashboardView(views.APIView):
    def get(self, request):
        # Check if the user is authenticated using the JWT token
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

        # Validate payload and retrieve user
        user_id = payload.get('id')
        if not user_id:
            logger.error("JWT payload does not contain 'id'.")
            return render(request, 'admin_login.html', {'error': 'Invalid token, please log in again.'}, status=401)

        user = User.objects.filter(id=user_id).first()
        if not user:
            logger.error("User not found for the given JWT payload.")
            return render(request, 'admin_login.html', {'error': 'User not found.'}, status=401)

        # Check if the user has admin access
        is_super_admin = user.is_superuser or (user.role and user.role.role_name == "Super Admin")
        is_system_admin = user.role and user.role.role_name == "System Admin"

        if not (is_super_admin or is_system_admin):
            logger.warning(f"Unauthorized access attempt by user {user.employee_number} with role {user.role.role_name if user.role else 'No Role'}.")
            return render(request, 'unauthorized_access.html')

        # Log user access
        logger.info(f"Authenticated user: {user.employee_number} with role {user.role.role_name if user.role else 'No Role'}. Accessing System Admin Dashboard.")
        logger.info(f"Is Super Admin: {is_super_admin}")
        logger.info(f"Is System Admin: {is_system_admin}")

        # Pass the user and role info to the template
        return render(request, 'system_admin_dashboard.html', {
            'user': user,
            'is_super_admin': is_super_admin,
            'is_system_admin': is_system_admin,
        })


# User View (for fetching authenticated user details)
class UserView(views.APIView):
    """
    Fetches details of the authenticated user
    """
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            logger.warning("Unauthorized attempt to fetch user details without a token.")
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            logger.info(f"JWT Decoded Payload for UserView: {payload}")  # Debugging JWT payload
        except jwt.ExpiredSignatureError:
            logger.error("Token expired for user details request.")
            raise AuthenticationFailed('Token has expired!')
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token during user details request: {e}")
            raise AuthenticationFailed('Invalid token!')

        user_id = payload.get('id')
        if not user_id:
            logger.error("JWT payload does not contain 'id'.")
            raise AuthenticationFailed('Invalid token!')

        user = User.objects.filter(id=user_id).first()
        if not user:
            logger.error("User not found for the given JWT payload in UserView.")
            raise AuthenticationFailed('User not found!')

        logger.info(f"Fetched authenticated user details for {user.employee_number}.")
        serializer = UserSerializer(user)
        return Response(serializer.data)

# Logout View
class LogoutView(views.APIView):
    """
    Handles user logout by deleting JWT token
    """
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response
