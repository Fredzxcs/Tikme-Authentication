from rest_framework import serializers
from .models import Employee
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _



class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'name', 'email', 'position']


# serializers.py
class SetupSecurityQuestionsSerializer(serializers.Serializer):
    security_question_1 = serializers.CharField(required=True)
    security_answer_1 = serializers.CharField(required=True)
    security_question_2 = serializers.CharField(required=True)
    security_answer_2 = serializers.CharField(required=True)
    security_question_3 = serializers.CharField(required=True)
    security_answer_3 = serializers.CharField(required=True)

    def save(self, user):
        user.security_question_1 = self.validated_data['security_question_1']
        user.security_answer_1 = self.validated_data['security_answer_1']
        user.security_question_2 = self.validated_data['security_question_2']
        user.security_answer_2 = self.validated_data['security_answer_2']
        user.security_question_3 = self.validated_data['security_question_3']
        user.security_answer_3 = self.validated_data['security_answer_3']
        user.account_status = 'active'
        user.save() 
        
class SetupPasswordSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(
        write_only=True, 
        style={'input_type': 'password'}, 
        max_length=128, 
        label="New Password"
    )
    new_password2 = serializers.CharField(
        write_only=True, 
        style={'input_type': 'password'}, 
        max_length=128, 
        label="Confirm Password"
    )

    def validate(self, attrs):
        """
        Validate that the two passwords match and comply with Django's password policies.
        """
        # Check if passwords match
        if attrs['new_password1'] != attrs['new_password2']:
            raise serializers.ValidationError("The two password fields must match.")

        # Use Django's built-in password validators
        try:
            validate_password(attrs['new_password1'])
        except serializers.ValidationError as e:
            # Return specific password validation errors
            raise serializers.ValidationError({
                'new_password1': list(e.messages)
            })
        
        return attrs

    def save(self, employee):
        """
        Save the new password to the employee instance.
        """
        # Update the employee's password
        employee.set_password(self.validated_data['new_password1'])
        employee.save()
        return employee