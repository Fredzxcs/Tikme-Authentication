from rest_framework import serializers
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
    class Meta:
        model = Permission
        fields = ['id', 'name']


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'role_name', 'permissions']


class JobTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobTitle
        fields = ['id', 'title_name']


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'status_name']


class QuestionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionList
        fields = ['id']

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SlugRelatedField(slug_field='role_name', queryset=Role.objects.all())
    module = serializers.SerializerMethodField()  # Use SerializerMethodField to get display values
    job_title = serializers.SerializerMethodField()
    status = serializers.SlugRelatedField(slug_field='status_name', queryset=Status.objects.all(), allow_null=True)


    class Meta:
        model = User
        fields = [
            'id', 'employee_number', 'email', 'password',
            'first_name', 'last_name', 'role', 'module', 'job_title',
            'status'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},  # Password is optional
        }

    def get_module(self, obj):
        return obj.module.module_name if obj.module else None

    def get_job_title(self, obj):
        return obj.job_title.title_name if obj.job_title else None
    
    def validate(self, data):
        """
        Validate user input:
        - Ensure only one Super Admin can exist.
        - Validate module and job title requirements based on role.
        """
        role = data.get('role')
        module = data.get('module')
        job_title = data.get('job_title')

        # Ensure only one Super Admin exists
        if role.role_name == "Super Admin":
            if self.instance:  # Update scenario
                if User.objects.filter(role__role_name="Super Admin").exclude(id=self.instance.id).exists():
                    raise serializers.ValidationError("Only one Super Admin is allowed.")
            else:  # Creation scenario
                if User.objects.filter(role__role_name="Super Admin").exists():
                    raise serializers.ValidationError("Only one Super Admin is allowed.")

        # Validate Module for certain roles
        if role.role_name in ["Manager", "Employee"] and not module:
            raise serializers.ValidationError(
                {"module": f"Module is required for the {role.role_name} role."}
            )
        if role.role_name == "System Admin" and module:
            raise serializers.ValidationError(
                {"module": "Module is not allowed for the System Admin role."}
            )

        # Ensure Job Title exists for roles where it's applicable
        if job_title and not JobTitle.objects.filter(title_name=job_title.title_name).exists():
            raise serializers.ValidationError(
                {"job_title": "The specified job title does not exist."}
            )

        return data

    def create(self, validated_data):
        """
        Custom create method to handle related fields (module, job_title).
        """
        module_data = validated_data.pop('module', None)
        job_title_data = validated_data.pop('job_title', None)
        user = super().create(validated_data)

        # Map module and job title
        if module_data:
            user.module = Module.objects.get(module_name=module_data)
        if job_title_data:
            user.job_title = JobTitle.objects.get(title_name=job_title_data)

        user.save()
        return user

    def update(self, instance, validated_data):
        """
        Custom update method to handle related fields (module, job_title).
        """
        module_data = validated_data.pop('module', None)
        job_title_data = validated_data.pop('job_title', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update module and job title
        if module_data:
            instance.module = Module.objects.get(module_name=module_data)
        if job_title_data:
            instance.job_title = JobTitle.objects.get(title_name=job_title_data)

        instance.save()
        return instance
