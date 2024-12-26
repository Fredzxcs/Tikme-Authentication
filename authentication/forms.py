from django import forms
from .models import *
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from django.conf import settings

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class TechSupportForm(forms.Form):
    full_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name',
        }),
        required=False,
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
        }),
        required=False,
    )
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number',
        }),
        required=False,
        validators=[
            RegexValidator(r'^\d{10,15}$', message='Enter a valid phone number.')
        ],
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Describe your issue in detail',
            'rows': 4,
        }),
        required=True,  # This field is required
    )
    attachments = forms.FileField(
        widget=MultipleFileInput(attrs={'multiple': True}),
        required=False,
    )

    def clean_attachments(self):
        files = self.files.getlist('attachments')
        allowed_types = getattr(settings, 'ALLOWED_FILE_TYPES', ['image/jpeg', 'image/png', 'application/pdf'])
        max_file_size = getattr(settings, 'MAX_FILE_SIZE_MB', 5) * 1024 * 1024  # Convert to bytes

        # Validate the number of files
        if len(files) > 3:
            raise forms.ValidationError("You can upload a maximum of 3 files.")

        # Define user-friendly names for file types
        readable_types = {
            'image/jpeg': 'JPEG',
            'image/png': 'PNG',
            'application/pdf': 'PDF',
        }
        allowed_type_names = [readable_types.get(file_type, file_type) for file_type in allowed_types]

        for file in files:
            # Validate empty files
            if file.size == 0:
                raise forms.ValidationError(f"File {file.name} is empty. Please upload a valid file.")

            # Validate file size
            if file.size > max_file_size:
                raise forms.ValidationError(f"File {file.name} exceeds the {settings.MAX_FILE_SIZE_MB}MB size limit.")

            # Validate file type
            if file.content_type not in allowed_types:
                raise forms.ValidationError(
                    f"{file.name} is not an allowed file type. Allowed types are: {', '.join(allowed_type_names)}."
                )

        return files
    
class SetupSecurityQuestionsForm(forms.Form):
    SECURITY_QUESTIONS = [
        ('What was the name of your first pet?', 'What was the name of your first pet?'),
        ('What was the model of your first car?', 'What was the model of your first car?'),
        ('In what city were you born?', 'In what city were you born?'),
        ('What was the name of your elementary school?', 'What was the name of your elementary school?'),
        ('What is your favorite book?', 'What is your favorite book?'),
        ('Who was your childhood hero?', 'Who was your childhood hero?'),
        ('What is the name of the street you grew up on?', 'What is the name of the street you grew up on?'),
        ('What was the make of your first smartphone?', 'What was the make of your first smartphone?'),
        ('What is your favorite food?', 'What is your favorite food?'),
        ('What is your mother\'s maiden name?', 'What is your mother\'s maiden name?'),
        ('What was the name of your first employer?', 'What was the name of your first employer?'),
        ('What is your favorite movie?', 'What is your favorite movie?'),
        ('What is your favorite place to visit?', 'What is your favorite place to visit?'),
        ('What is the name of your favorite childhood teacher?', 'What is the name of your favorite childhood teacher?'),
        ('What was your dream job as a child?', 'What was your dream job as a child?'),
        ('What was the name of your first best friend?', 'What was the name of your first best friend?'),
        ('What is the name of your favorite sports team?', 'What is the name of your favorite sports team?'),
        ('What was your high school mascot?', 'What was your high school mascot?'),
        ('What is the name of your favorite restaurant?', 'What is the name of your favorite restaurant?'),
        ('What is your favorite hobby?', 'What is your favorite hobby?'),
    ]

    security_question_1 = forms.ChoiceField(choices=SECURITY_QUESTIONS, label="Security Question 1")
    security_answer_1 = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Type your answer here...'}))

    security_question_2 = forms.ChoiceField(choices=SECURITY_QUESTIONS, label="Security Question 2")
    security_answer_2 = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Type your answer here...'}))

    security_question_3 = forms.ChoiceField(choices=SECURITY_QUESTIONS, label="Security Question 3")
    security_answer_3 = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Type your answer here...'}))

    def clean(self):
        cleaned_data = super().clean()
        question_1 = cleaned_data.get('security_question_1')
        question_2 = cleaned_data.get('security_question_2')
        question_3 = cleaned_data.get('security_question_3')

        # Check for duplicate questions
        if len({question_1, question_2, question_3}) < 3:
            raise forms.ValidationError("Please select unique security questions.")

        return cleaned_data

class SetupPasswordForm(forms.Form):
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your new password',
            'class': 'form-control'
        }),
        max_length=128,
        strip=False,
        required=True,
        help_text="Enter a new password."
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm your new password',
            'class': 'form-control'
        }),
        max_length=128,
        strip=False,
        required=True,
        help_text="Enter the same password as before."
    )


    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields must match.")

        validate_password(password1)  # Validate password strength

        return cleaned_data