from rest_framework.response import Response
from rest_framework import status, views
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from django.conf import settings
from django.shortcuts import get_object_or_404
from ..models import *
from ..serializers import *
import jwt


class ModuleListCreateView(views.APIView):
    def get(self, request):
        modules = Module.objects.all()
        serializer = ModuleSerializer(modules, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ModuleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RoleListCreateView(views.APIView):
    def get(self, request):
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StatusListCreateView(views.APIView):
    def get(self, request):
        statuses = Status.objects.all()
        serializer = StatusSerializer(statuses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = StatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class JobTitleListCreateView(views.APIView):
    """
    Handles listing and creating job titles.
    """
    def get(self, request):
        job_titles = JobTitle.objects.all()
        serializer = JobTitleSerializer(job_titles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = JobTitleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class StatusDetailView(views.APIView):
    def get(self, request, pk):
        status_instance = get_object_or_404(Status, pk=pk)
        serializer = StatusSerializer(status_instance)
        return Response(serializer.data)

    def put(self, request, pk):
        status_instance = get_object_or_404(Status, pk=pk)
        serializer = StatusSerializer(status_instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        status_instance = get_object_or_404(Status, pk=pk)
        status_instance.delete()
        return Response({'message': 'Status deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

class QuestionsListCreateView(views.APIView):
    """
    Handles listing and creating questions.
    """
    def get(self, request):
        questions = Question.objects.all()
        serializer = QuestionsSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = QuestionsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class QuestionsDetailView(views.APIView):
    """
    Handles retrieving, updating, and deleting a single question.
    """
    def get(self, request, pk):
        question = get_object_or_404(Question, pk=pk)
        serializer = QuestionsSerializer(question)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        question = get_object_or_404(Question, pk=pk)
        serializer = QuestionsSerializer(question, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        question = get_object_or_404(Question, pk=pk)
        question.delete()
        return Response({'message': 'Question deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

class EmployeeListCreateView(views.APIView):
    """
    Handles listing and creating employees.
    """
    def get(self, request):
        employees = User.objects.all()
        serializer = UserSerializer(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.set_password(request.data['password'])  # Hash the password
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class EmployeeDetailView(views.APIView):
    """
    Handles retrieving, updating, and deleting a single employee.
    """
    def get(self, request, pk):
        employee = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(employee)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        employee = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(employee, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        employee = get_object_or_404(User, pk=pk)
        employee.delete()
        return Response({'message': 'Employee deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
class UserListCreateView(views.APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.set_password(request.data['password'])  # Hash the password
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserDetailView(views.APIView):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class ManageUsersView(views.APIView):
    """
    View to manage users based on the role of the authenticated user.
    """
    def get(self, request):
        # Check JWT authentication
        token = request.COOKIES.get('jwt')
        if not token:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired!')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token!')

        # Fetch user and validate role
        user = User.objects.filter(id=payload['id']).first()
        if not user:
            raise AuthenticationFailed('User not found!')

        if user.role.role_name == 'Super Admin':
            users = User.objects.all()  # Super Admin can access all users
        elif user.role.role_name == 'System Admin':
            users = User.objects.filter(role__role_name__in=['Manager', 'Employee'])  # System Admin restricted access
        else:
            raise PermissionDenied('You do not have permission to access this resource.')

        # Serialize and return the list of users
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AddUserView(views.APIView):
    def post(self, request):
        # Check JWT authentication
        token = request.COOKIES.get('jwt')
        if not token:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired!')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token!')

        # Fetch user and validate role
        user = User.objects.filter(id=payload['id']).first()
        if not user:
            raise AuthenticationFailed('User not found!')

        # Role-based authorization
        role = request.data.get('role')
        if user.role.role_name == 'Super Admin':
            allowed_roles = ['Super Admin', 'System Admin', 'Manager', 'Employee']
        elif user.role.role_name == 'System Admin':
            allowed_roles = ['Manager', 'Employee']
        else:
            raise PermissionDenied('You do not have permission to add users.')

        if role not in allowed_roles:
            return Response({'error': f'Invalid role. Allowed roles: {", ".join(allowed_roles)}'}, status=status.HTTP_403_FORBIDDEN)

        # Serialize and save user
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_user = serializer.save()
        new_user.set_password(request.data['password'])  # Hash password
        new_user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class EditUserView(views.APIView):
    def put(self, request, pk):
        token = request.COOKIES.get('jwt')
        if not token:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired!')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token!')

        user = User.objects.filter(id=payload['id']).first()
        if not user:
            raise AuthenticationFailed('User not found!')

        # Authorization check
        target_user = get_object_or_404(User, pk=pk)
        if user.role.role_name != 'Super Admin' and target_user.role.role_name not in ['Manager', 'Employee']:
            raise PermissionDenied('You do not have permission to edit this user.')

        serializer = UserSerializer(target_user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

class DeleteUserView(views.APIView):
    def delete(self, request, pk):
        token = request.COOKIES.get('jwt')
        if not token:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired!')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token!')

        user = User.objects.filter(id=payload['id']).first()
        if not user:
            raise AuthenticationFailed('User not found!')

        target_user = get_object_or_404(User, pk=pk)
        if user.role.role_name != 'Super Admin':
            raise PermissionDenied('You do not have permission to delete this user.')

        target_user.delete()
        return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
