from rest_framework import serializers
from .models import *


class ModuleSerializer(serializers.ModelSerializer):  # Corrected from ModulesSerializer
    class Meta:
        model = Module  # Corrected from Modules
        fields = ['id', 'module_name']  # Corrected field name from name to module_name


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role  # Corrected from Roles
        fields = ['id', 'role_name']


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'status_name']


class QuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question  # Corrected from Questions
        fields = ['id', 'description']  # Corrected field name from question_desc to description


class QuestionListSerializer(serializers.ModelSerializer):
    questions = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all(), many=True)

    class Meta:
        model = QuestionList
        fields = ['id', 'questions']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class JobTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobTitle
        fields = ['id', 'title_name']


class UserSerializer(serializers.ModelSerializer):
    status = StatusSerializer()
    question_list = QuestionListSerializer()
    role = RoleSerializer()
    module = ModuleSerializer()
    job_title = JobTitleSerializer()

    class Meta:
        model = User
        fields = [
            'id',
            'employee_number',
            'name',
            'email',
            'password',
            'role',
            'status',
            'question_list',
            'module',
            'job_title',
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Handle nested serializers
        status_data = validated_data.pop('status', None)
        question_list_data = validated_data.pop('question_list', None)
        role_data = validated_data.pop('role', None)
        module_data = validated_data.pop('module', None)
        job_title_data = validated_data.pop('job_title', None)

        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()

        if status_data:
            status = Status.objects.create(**status_data)
            user.status = status

        if question_list_data:
            questions = question_list_data.pop('questions', [])
            question_list = QuestionList.objects.create()
            question_list.questions.set(questions)
            question_list.save()
            user.question_list = question_list

        if role_data:
            role = Role.objects.create(**role_data)
            user.role = role

        if module_data:
            module = Module.objects.create(**module_data)
            user.module = module

        if job_title_data:
            job_title = JobTitle.objects.create(**job_title_data)
            user.job_title = job_title

        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance
