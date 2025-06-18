from django.core.management.base import BaseCommand
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Configure les dossiers media nécessaires'

    def handle(self, *args, **options):
        # Créer le dossier media s'il n'existe pas
        media_root = settings.MEDIA_ROOT
        if not os.path.exists(media_root):
            os.makedirs(media_root)
            self.stdout.write(self.style.SUCCESS(f'Dossier media créé : {media_root}'))
        
        # Créer le dossier credentials s'il n'existe pas
        credentials_dir = os.path.join(media_root, 'credentials')
        if not os.path.exists(credentials_dir):
            os.makedirs(credentials_dir)
            self.stdout.write(self.style.SUCCESS(f'Dossier credentials créé : {credentials_dir}'))
        
        self.stdout.write(self.style.SUCCESS('Configuration des dossiers media terminée avec succès')) 