from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0090_alter_person_options"),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                "ALTER TABLE members_person "
                "ADD COLUMN IF NOT EXISTS allow_contact_from_cpdk boolean NOT NULL DEFAULT false;"
            ),
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql=(
                "ALTER TABLE members_person "
                "ADD COLUMN IF NOT EXISTS allow_contact_from_other boolean NOT NULL DEFAULT false;"
            ),
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql=(
                "ALTER TABLE members_volunteer "
                "DROP COLUMN IF EXISTS allow_cpdk_contact;"
            ),
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
