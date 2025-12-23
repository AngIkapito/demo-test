# Revised to safely enforce FK: allow NULL, clean data, then add constraint

from django.db import migrations, models
import django.db.models.deletion


def null_invalid_registered_by(apps, schema_editor):
    Bulk = apps.get_model('app', 'Bulk_Event_Reg')
    Member = apps.get_model('app', 'Member')

    valid_ids = list(Member.objects.values_list('id', flat=True))
    (Bulk.objects
         .filter(registered_by_id__isnull=False)
         .exclude(registered_by_id__in=valid_ids)
         .update(registered_by=None))


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0048_bulk_event_reg_email'),
    ]

    operations = [
        # 1) Drop/avoid FK constraint and allow NULLs to enable cleanup
        migrations.AlterField(
            model_name='bulk_event_reg',
            name='registered_by',
            field=models.ForeignKey(
                to='app.member',
                on_delete=django.db.models.deletion.SET_NULL,
                null=True,
                blank=True,
                db_constraint=False,
            ),
        ),
        # 2) Clean invalid rows that point to non-existent members
        migrations.RunPython(null_invalid_registered_by, migrations.RunPython.noop),
        # 3) Re-add FK constraint now that data is clean
        migrations.AlterField(
            model_name='bulk_event_reg',
            name='registered_by',
            field=models.ForeignKey(
                to='app.member',
                on_delete=django.db.models.deletion.SET_NULL,
                null=True,
                blank=True,
                db_constraint=True,
            ),
        ),
    ]
