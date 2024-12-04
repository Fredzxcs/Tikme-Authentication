from django.db import migrations
from django.contrib.auth.models import Group, Permission

def create_groups(apps, schema_editor):
    # Create system admin group if it doesn't exist
    system_admin_group, created = Group.objects.get_or_create(name='System Admin')

    # Create employee group if it doesn't exist
    employee_group, created = Group.objects.get_or_create(name='Employee')

    # Fetch all permissions
    all_permissions = Permission.objects.all()

    # Assign all permissions to both groups
    system_admin_group.permissions.set(all_permissions)
    employee_group.permissions.set(all_permissions)

    # Save the groups
    system_admin_group.save()
    employee_group.save()

class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),  # Adjust this depending on your existing migrations
    ]

    operations = [
        migrations.RunPython(create_groups),
    ]
