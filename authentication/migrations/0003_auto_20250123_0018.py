from django.db import migrations, models


def populate_status(apps, schema_editor):
    Status = apps.get_model('authentication', 'Status')

    # Use the correct field 'status_name' for inserting status values
    Status.objects.get_or_create(status_name="Pending")
    Status.objects.get_or_create(status_name="Active")
    Status.objects.get_or_create(status_name="Inactive")
    Status.objects.get_or_create(status_name="Suspended")


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_auto_20250122_1606'),  # Update to your last migration
    ]

    operations = [
        # Populate status_name automatically without adding a conflicting field
        migrations.RunPython(populate_status),
    ]
