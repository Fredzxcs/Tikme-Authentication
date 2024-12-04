from django import forms
from .models import Employee
from django.contrib.auth.password_validation import validate_password



class TechSupportForm(forms.Form):
    full_name = forms.CharField(label='Full Name', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Email Address', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(label='Phone Number (optional)', max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    issue_description = forms.CharField(label='Please describe your issue in detail.', widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}))
    attachment = forms.FileField(label='Attach screenshots or documents to help us understand your issue better.', required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

class EmployeeCreationForm(forms.ModelForm):
    class Meta: 
        model = Employee
        fields = ('username', 'email', 'first_name', 'last_name', 'job_title', 'role')
    # Explicitly ensuring role is selected; otherwise, defaults to employee.
    role = forms.ChoiceField(choices=Employee._meta.get_field('role').choices, required=True)
        
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