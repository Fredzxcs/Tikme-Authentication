from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Permission
from .models import *


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id', 'module_name']

    def validate_module_name(self, value):
        if Module.objects.filter(module_name__iexact=value).exists():
            raise serializers.ValidationError("A module with this name already exists.")
        return value

class PermissionSerializer(serializers.ModelSerializer):
    """ ✅ Fetches permissions from Django's auth_permission table """
    class Meta:
        model = Permission  # ✅ Now using Django's built-in Permission model
        fields = ['id', 'name', 'codename']  # ✅ Includes codename for better control

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'role_name']


class JobTitleSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(), many=True
    )  # ✅ Now correctly fetching from Django's built-in auth_permission table

    class Meta:
        model = JobTitle
        fields = ['id', 'title_name', 'permissions']


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'status_name']


class SecurityQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityQuestion
        fields = ['id', 'question_text']


class SecurityAnswerSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(queryset=SecurityQuestion.objects.all())

    class Meta:
        model = SecurityAnswer
        fields = ['id', 'question', 'answer']

    def validate(self, data):
        # Check if answer is provided
        if not data.get('answer'):
            raise serializers.ValidationError({"answer": "An answer is required for the security question."})
        return data

class SetupPasswordSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(write_only=True, required=True)
    new_password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        # Check if passwords match
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({"new_password2": "Passwords do not match."})
        # Validate password strength
        validate_password(data['new_password1'])
        return data

    def save(self, user):
        user.set_password(self.validated_data['new_password1'])
        user.save()

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SlugRelatedField(slug_field='role_name', queryset=Role.objects.all())
    module = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    job_title = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    status = serializers.SlugRelatedField(slug_field='status_name', queryset=Status.objects.all(), allow_null=True)
    security_answers = SecurityAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'employee_number', 'email', 'password',
            'first_name', 'last_name', 'role', 'module', 'job_title',
            'status', 'security_answers'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
        }

    def validate(self, data):
        role = data.get('role')
        module_name = data.get('module')
        job_title_name = data.get('job_title')

        # Ensure only one Super Admin exists
        if role.role_name == "Super Admin":
            if self.instance:
                if User.objects.filter(role__role_name="Super Admin").exclude(id=self.instance.id).exists():
                    raise serializers.ValidationError("Only one Super Admin is allowed.")
            else:
                if User.objects.filter(role__role_name="Super Admin").exists():
                    raise serializers.ValidationError("Only one Super Admin is allowed.")

        # Validate module and role requirements
        if role.role_name in ["Manager", "Employee"] and not module_name:
            raise serializers.ValidationError(f"Module is required for the {role.role_name} role.")
        if role.role_name == "System Admin" and module_name:
            raise serializers.ValidationError("Module is not allowed for the System Admin role.")

        # Validate the existence of module and job title
        if module_name and not Module.objects.filter(module_name=module_name).exists():
            raise serializers.ValidationError(f"Module '{module_name}' does not exist.")
        if job_title_name and not JobTitle.objects.filter(title_name=job_title_name).exists():
            raise serializers.ValidationError(f"Job title '{job_title_name}' does not exist.")

        return data

    def create(self, validated_data):
        module_name = validated_data.pop('module', None)
        job_title_name = validated_data.pop('job_title', None)
        user = super().create(validated_data)

        if module_name:
            user.module = Module.objects.get(module_name=module_name)
        if job_title_name:
            user.job_title = JobTitle.objects.get(title_name=job_title_name)

        user.save()
        return user

    def update(self, instance, validated_data):
        # Check for duplicate employee_number only if it is being updated
        if 'employee_number' in validated_data:
            employee_number = validated_data['employee_number']
            if employee_number != instance.employee_number:
                if User.objects.filter(employee_number=employee_number).exclude(id=instance.id).exists():
                    raise serializers.ValidationError({'employee_number': 'User with this employee number already exists.'})

        # Check for duplicate email only if it is being updated
        if 'email' in validated_data:
            email = validated_data['email']
            if email != instance.email:
                if User.objects.filter(email=email).exclude(id=instance.id).exists():
                    raise serializers.ValidationError({'email': 'User with this email already exists.'})

        # Handle module and job title updates
        module_name = validated_data.pop('module', None)
        job_title_name = validated_data.pop('job_title', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if module_name:
            instance.module = Module.objects.get(module_name=module_name)
        else:
            instance.module = None  # Clear the module if not provided
        if job_title_name:
            instance.job_title = JobTitle.objects.get(title_name=job_title_name)
        else:
            instance.job_title = None  # Clear the job title if not provided

        instance.save()
        return instance

