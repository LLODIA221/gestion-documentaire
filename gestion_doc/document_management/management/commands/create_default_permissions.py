from django.core.management.base import BaseCommand
from ...models import Permission

class Command(BaseCommand):
    help = 'Crée toutes les permissions de base pour chaque entité et action standard.'

    def handle(self, *args, **options):
        entities = [
            'DELEGATION', 'STRUCTURE', 'AGENTS', 'DOCUMENTS', 'ROLES', 'CATEGORIE_DOCUMENTS',
            'PERMISSIONS', 'USERS', 'JOURNAUX', 'DEMANDES', 'NOTIFICATIONS'
        ]
        actions = ['CREATE', 'READ', 'UPDATE', 'DELETE', 'ALL']
        count = 0
        for entity in entities:
            for action in actions:
                obj, created = Permission.objects.get_or_create(entity=entity, action=action)
                if created:
                    count += 1
        self.stdout.write(self.style.SUCCESS(f'{count} permissions créées ou déjà existantes.')) 