from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from ..models import *
from ..serializers import *
import jwt, datetime
import requests
from django.shortcuts import render
from rest_framework import status, views

# Create your views here.
class RegisterView(views.APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(views.APIView):
    def post(self, request):
        employee_number = request.data['employee_number']
        password = request.data['password']

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
            'exp': current_time + datetime.timedelta(minutes=60),  # Token expires in 60 minutes
            'iat': current_time,  # Token issued at current time
            'nbf': current_time,  # Token valid from current time
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        if user.modules == 'Reservations':
            redirection_url = '/reservations-dashboard'
        if user.modules == 'Logistics':
            redirection_url = '/logistics-dashboard'
        if user.modules == 'Finance':
            redirection_url = 'http://127.0.0.1:8001/dashboard/'
        if user.modules == None:
            redirection_url = '/no-access'

        # Prepare role information
        role_data = None
        if user.roles_FK:
            role_data = {
                'id': user.roles_FK.id,
                'role_name': user.roles_FK.role_name
            }

        # Response with token, role, and redirection URL
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token,
            'role': role_data,  # Role information from `Roles`
            'module': user.modules,  # Assigned module for this user instance
            'redirect_to': redirection_url,  # Redirection URL
        }
        return response


class UserView(views.APIView):
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