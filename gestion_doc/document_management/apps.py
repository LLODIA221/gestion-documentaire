from django.apps import AppConfig
from django.core.management import call_command
import os


class DocumentManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'document_management'

    def ready(self):
        # Exécuter uniquement lors du runserver, pas lors des migrations ou du shell
        if os.environ.get('RUN_MAIN') == 'true':
            try:
                call_command('create_default_permissions')
                call_command('create_default_users')
                call_command('setup_media')
            except Exception as e:
                # On ignore les erreurs pour ne pas bloquer le serveur
                pass
