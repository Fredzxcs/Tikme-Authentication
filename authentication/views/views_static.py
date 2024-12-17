from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from ..serializers import UserSerializer
import jwt, datetime
import requests
from django.shortcuts import render

def landing_page(request):
    return render(request, 'admin_login.html')

def forgot_pass(request):
    return render(request, 'forgot_password.html')

def tech_support(request):
    return render(request, 'tech_support.html')

def success_page(request):
    return render(request, 'system_admin_login.html')
