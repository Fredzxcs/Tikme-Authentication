from django import forms
from .models import *
from django.contrib.auth.forms import UserChangeForm
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

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "Enter your email", "class": "input-field"}),
    )
    

class SetupSecurityQuestionsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Fetch questions from the database
        questions = SecurityQuestion.objects.all()
        question_choices = [(q.id, q.question_text) for q in questions]
        
        self.fields['security_question_1'] = forms.ChoiceField(
            choices=question_choices, label="Security Question 1"
        )
        self.fields['security_answer_1'] = forms.CharField(
            max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Type your answer here...'})
        )
        self.fields['security_question_2'] = forms.ChoiceField(
            choices=question_choices, label="Security Question 2"
        )
        self.fields['security_answer_2'] = forms.CharField(
            max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Type your answer here...'})
        )
        self.fields['security_question_3'] = forms.ChoiceField(
            choices=question_choices, label="Security Question 3"
        )
        self.fields['security_answer_3'] = forms.CharField(
            max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Type your answer here...'})
        )

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
    
class AccountSettingsForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'profile_picture']

    def clean_profile_picture(self):
        """
        Ensure that the uploaded image is of the correct size and type.
        """
        profile_picture = self.cleaned_data.get('profile_picture')

        if profile_picture:
            max_size = 5 * 1024 * 1024  # 5MB max size
            if profile_picture.size > max_size:
                raise forms.ValidationError("Profile picture size exceeds the 5MB limit.")
            
            allowed_formats = ['image/jpeg', 'image/png']
            if profile_picture.content_type not in allowed_formats:
                raise forms.ValidationError("Invalid file type. Allowed types: JPEG, PNG.")
        
        return profile_picture