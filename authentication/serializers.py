from rest_framework import serializers
from .models import User, Status, QuestionList, Questions


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'status_name']


class QuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questions
        fields = ['id', 'question_desc']


class QuestionListSerializer(serializers.ModelSerializer):
    questions_FK = QuestionsSerializer()

    class Meta:
        model = QuestionList
        fields = ['id', 'questions_FK']


class UserSerializer(serializers.ModelSerializer):
    status_FK = StatusSerializer()  # Nested serializer for Status
    question_list_FK = QuestionListSerializer()  # Nested serializer for QuestionList

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'employee_number', 'password', 'status_FK', 'question_list_FK']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Handle nested serializers if needed
        status_data = validated_data.pop('status_FK', None)
        question_list_data = validated_data.pop('question_list_FK', None)
        
        user = User(**validated_data)
        user.set_password(validated_data['password'])  # Hash password
        user.save()

        if status_data:
            status = Status.objects.create(**status_data)
            user.status_FK = status

        if question_list_data:
            questions_data = question_list_data.pop('questions_FK', None)
            if questions_data:
                questions = Questions.objects.create(**questions_data)
                question_list = QuestionList.objects.create(questions_FK=questions)
                user.question_list_FK = question_list

        user.save()
        return user
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance