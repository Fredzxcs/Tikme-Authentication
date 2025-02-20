from django.db import migrations

def assign_permissions_to_super_admin(apps, schema_editor):
    JobTitle = apps.get_model('authentication', 'JobTitle')
    Permission = apps.get_model('auth', 'Permission')

    # Ensure Super Admin job title exists
    super_admin_title, created = JobTitle.objects.get_or_create(title_name="Super Admin")

    # Assign all permissions
    all_permissions = Permission.objects.all()
    super_admin_title.permissions.set(all_permissions)
    super_admin_title.save()

    print(f"✅ Super Admin now has {super_admin_title.permissions.count()} permissions.")

class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(assign_permissions_to_super_admin),
    ]
