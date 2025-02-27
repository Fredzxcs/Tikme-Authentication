from django.contrib.auth.models import BaseUserManager
from django.apps import apps
import random

class UserManager(BaseUserManager):

    def generate_unique_user_number(self, prefix, length=4):
        """ Generate a unique user number ensuring it does not exist in the database """
        from .models import User  # Avoid circular imports

        while True:
            random_number = random.randint(1000, 9999)
            user_number = f"{prefix}-{random_number}"
            if not User.objects.filter(user_number=user_number).exists():
                return user_number

    def generate_super_admin_code(self):
        """ Generate a unique user number for Super Admins """
        return self.generate_unique_user_number("SUP")

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        Role = apps.get_model('authentication', 'Role')
        Status = apps.get_model('authentication', 'Status')
        SecurityQuestion = apps.get_model('authentication', 'SecurityQuestion')

        # ✅ Auto-assign role and status for Super Admin
        extra_fields['role'], _ = Role.objects.get_or_create(role_name='Super Admin')
        extra_fields['status'], _ = Status.objects.get_or_create(status_name='Active')

        # ✅ REMOVE `user_number` from `createsuperuser` prompt
        extra_fields.pop('user_number', None)

        # ✅ Auto-generate `user_number`
        user_number = self.generate_super_admin_code()

        # ✅ Prompt for **THREE** Security Questions
        questions = list(SecurityQuestion.objects.all())
        if len(questions) < 3:
            raise ValueError("At least 3 Security Questions are required! Run migrations.")

        print("\n📌 Choose 3 Security Questions:\n")
        for idx, question in enumerate(questions, 1):
            print(f"{idx}. {question.question_text}")

        selected_questions = []
        for i in range(3):
            while True:
                selected_question = input(f"\nEnter question {i+1} number: ")
                try:
                    selected_question = int(selected_question)
                    if 1 <= selected_question <= len(questions) and questions[selected_question - 1] not in selected_questions:
                        selected_questions.append(questions[selected_question - 1])
                        break
                    else:
                        print("❌ Invalid selection. Please enter a unique valid question number.")
                except ValueError:
                    print("❌ Invalid input. Please enter a valid number.")

        security_answers = []
        for question in selected_questions:
            answer = input(f"Enter your answer for '{question.question_text}': ").strip().lower()
            while not answer:
                print("❌ Security Answer is required.")
                answer = input(f"Enter your answer for '{question.question_text}': ").strip().lower()
            security_answers.append((question, answer))

        # ✅ Create Super Admin
        user = self.model(
            user_number=user_number,
            email=self.normalize_email(email),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        # ✅ Save Security Questions & Answers
        SecurityAnswer = apps.get_model('authentication', 'SecurityAnswer')
        for question, answer in security_answers:
            SecurityAnswer.objects.create(user=user, question=question, answer=answer)

        print(f"\n✅ Super Admin Created Successfully!\nUser Number: {user_number}\n")

        return user

    def get_by_natural_key(self, user_number):
        """ Ensures that Django's authentication system correctly retrieves users by user_number """
        return self.get(user_number=user_number)

    def get_input_fields(self, user, **kwargs):
        """ Exclude `user_number` from prompts in `createsuperuser` """
        fields = super().get_input_fields(user, **kwargs)
        return [field for field in fields if field != "user_number"]
