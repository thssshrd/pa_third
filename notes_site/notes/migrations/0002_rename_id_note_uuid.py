# Generated by Django 5.1.3 on 2024-11-25 21:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='note',
            old_name='id',
            new_name='uuid',
        ),
    ]
