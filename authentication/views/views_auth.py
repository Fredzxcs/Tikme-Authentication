from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.exceptions import AuthenticationFailed
from ..models import *
from ..serializers import *
import jwt, datetime
import requests
# from django.shortcuts import render
from rest_framework import status, views
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import NotFound

# Create your views here.
class RegisterView(views.APIView):
    def get(self, request):
        user = User.objects.all()
        serializer = UserSerializer(user, many=True)
        return JsonResponse(serializer.data, safe=False)
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return JsonResponse(serializer.data)

class RegisterViewRUD(views.APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise NotFound(detail="User not found", code=404)
    
    def put(self, request, pk):
        # Update entire user object
        user = self.get_object(pk)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return JsonResponse(serializer.data)

    def patch(self, request, pk):
        # Partially update user object
        user = self.get_object(pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return JsonResponse(serializer.data)

    def delete(self, request, pk):
        # Delete user
        user = self.get_object(pk)
        user.delete()
        return JsonResponse({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class LoginView(views.APIView):
    def post(self, request):
        employee_number = request.data['employee_number']
        password = request.data['password']
        redirection_url = 'http://127.0.0.1:8000/admin_login/'

        # Authenticate user
        user = User.objects.filter(employee_number=employee_number).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')

        # Generate JWT token
        current_time = datetime.datetime.now()
        payload = {
            'id': user.id,
            'exp': current_time + datetime.timedelta(minutes=60),
            'iat': current_time,
            'nbf': current_time,
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        # Determine redirection URL based on user modules
        if user.modules_FK == 'Reservations':
            redirection_url = 'http://127.0.0.1:8000/success/'
        elif user.modules_FK == 'Logistics':
            redirection_url = '/logistics-dashboard'
        elif user.modules_FK == 'Finance':
            redirection_url = 'http://127.0.0.1:8001/dashboard/'
        elif user.modules_FK == 'None':
            redirection_url = '/no-access'

        # Prepare role information
        user_data = None
        if user.roles_FK:  # Check if a role is assigned
            user_data = {
                'id': user.roles_FK.id,
                'user_name': user.name,
                'user': user.employee_number,
                'role_name': user.roles_FK.role_name,
                'module': user.modules_FK.module_assign,
            }

        # Response with token, role, and redirection URL
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token,
            'data': user_data,
            'redirect_to': redirection_url,
        }
        return response


class UserView(views.APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'], options={'verify_exp': True, 'verify_iat': True})
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired!')
        except jwt.ImmatureSignatureError:
            raise AuthenticationFailed('Token is not yet valid (iat)!')

        user = User.objects.filter(id=payload['id']).first()
        if not user:
            raise AuthenticationFailed('User not found!')

        serializer = UserSerializer(user)
        return Response(serializer.data)


class LogoutView(views.APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response