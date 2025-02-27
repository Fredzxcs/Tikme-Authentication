from django.db import migrations
import random
from django.contrib.auth.hashers import make_password

def create_super_admin(apps, schema_editor):
    User = apps.get_model("authentication", "User")
    Role = apps.get_model("authentication", "Role")
    Status = apps.get_model("authentication", "Status")
    SecurityQuestion = apps.get_model("authentication", "SecurityQuestion")
    SecurityAnswer = apps.get_model("authentication", "SecurityAnswer")

    # ✅ Check if Super Admin already exists
    if User.objects.filter(is_superuser=True).exists():
        print("\n✅ Super Admin already exists. Skipping creation.")
        return

    print("\n🚀 Creating Super Admin user...")

    # ✅ Generate a unique Super Admin user number
    while True:
        user_number = f"SUP-{random.randint(1000, 9999)}"
        if not User.objects.filter(user_number=user_number).exists():
            break

    # ✅ Auto-assign Super Admin role & status
    super_admin_role, _ = Role.objects.get_or_create(role_name="Super Admin")
    active_status, _ = Status.objects.get_or_create(status_name="Active")

    # ✅ Create Super Admin User
    super_admin = User.objects.create(
        user_number=user_number,
        email="tikmedinesupp@gmail.com",
        first_name="John Frederick",
        last_name="Sabondo",
        role=super_admin_role,
        status=active_status,
        is_staff=True,
        is_superuser=True,
        password=make_password("minmax0812")  # ✅ Manually hash password
    )

    print(f"\n✅ Super Admin Created!\nUser Number: {user_number}\nEmail: {super_admin.email}\n")

    # ✅ Predefine security questions and answers
    predefined_questions = {
        "What was the name of your first pet?": "dyesebel",
        "What was the model of your first car?": "ford",
        "In what city were you born?": "quezon"
    }

    for question_text, answer in predefined_questions.items():
        question, created = SecurityQuestion.objects.get_or_create(question_text=question_text)
        SecurityAnswer.objects.create(user=super_admin, question=question, answer=answer)

    print("\n✅ Security Questions & Answers assigned successfully!")

class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0007_user_failed_attempts_user_is_permanently_locked_and_more"),
    ]

    operations = [
        migrations.RunPython(create_super_admin),
    ]
