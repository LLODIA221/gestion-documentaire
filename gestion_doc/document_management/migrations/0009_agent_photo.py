# Generated by Django 5.1.7 on 2025-06-13 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document_management', '0008_alter_role_options_alter_role_libelle'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='photo',
            field=models.ImageField(blank=True, help_text="Photo de profil de l'agent", null=True, upload_to='agents/photos/', verbose_name='Photo'),
        ),
    ]
