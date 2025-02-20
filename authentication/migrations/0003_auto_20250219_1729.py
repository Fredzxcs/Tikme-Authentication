from django.db import migrations

def populate_security_questions(apps, schema_editor):
    SecurityQuestion = apps.get_model("authentication", "SecurityQuestion")

    questions = [
        "What was the name of your first pet?",
        "What was the model of your first car?",
        "In what city were you born?",
        "What was the name of your elementary school?",
        "What is your favorite book?",
        "Who was your childhood hero?",
        "What is the name of the street you grew up on?",
        "What was the make of your first smartphone?",
        "What is your favorite food?",
        "What is your mother's maiden name?",
        "What was the name of your first employer?",
        "What is your favorite movie?",
        "What is your favorite place to visit?",
        "What is the name of your favorite childhood teacher?",
        "What was your dream job as a child?",
        "What was the name of your first best friend?",
        "What is the name of your favorite sports team?",
        "What was your high school mascot?",
        "What is the name of your favorite restaurant?",
        "What is your favorite hobby?",
    ]

    for question in questions:
        SecurityQuestion.objects.get_or_create(question_text=question)

class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0002_assign_super_admin_permissions"),
    ]

    operations = [
        migrations.RunPython(populate_security_questions),
    ]