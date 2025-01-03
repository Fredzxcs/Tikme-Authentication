from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from ..serializers import UserSerializer
import jwt, datetime
import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def forgot_pass(request):
    return render(request, 'forgot_password.html')

def tech_support(request):
    return render(request, 'tech_support.html')

def success_page(request):
    return render(request, 'admin_login.html')

def unauthorized_access(request):
    return render(request, 'unauthorized_access.html')

