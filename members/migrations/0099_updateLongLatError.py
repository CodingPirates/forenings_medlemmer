from django.db import migrations

def reset_longLat(apps, schema_editor):
    Department = apps.get_model('members', 'Department')
    deps = Department.objects.all()
    for dep in deps:
        dep.longtitude = None
        dep.latitude = None
        dep.save()

class Migration(migrations.Migration):
    dependencies = [
        ('members', '0098_auto_20170711_1235'),
    ]

    operations = [
        migrations.RunPython(reset_longLat),
    ]
