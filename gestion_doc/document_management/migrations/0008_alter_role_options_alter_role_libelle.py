# Generated by Django 5.1.7 on 2025-05-25 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document_management', '0007_alter_role_options_alter_role_libelle'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='role',
            options={'ordering': ['niveau'], 'verbose_name': 'Rôle', 'verbose_name_plural': 'Rôles'},
        ),
        migrations.AlterField(
            model_name='role',
            name='libelle',
            field=models.CharField(choices=[('ADMIN', 'Administrateur'), ('AGENT', 'Agent'), ('GESTIONNAIRE', 'Gestionnaire'), ('CONTROLLER', 'Contrôleur')], max_length=20, unique=True, verbose_name='Libellé'),
        ),
    ]
