# Generated by Django 5.1.7 on 2025-03-27 16:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document_management', '0002_remove_delegation_code_remove_delegation_is_active_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='structure',
            name='delegation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='structures', to='document_management.delegation', verbose_name='Délégation'),
        ),
    ]
