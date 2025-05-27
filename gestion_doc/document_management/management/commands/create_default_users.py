from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from document_management.models import Agent, Role, Structure

class Command(BaseCommand):
    help = 'Crée un superutilisateur (admin) et un gestionnaire par défaut avec matricule.'

    def handle(self, *args, **options):
        User = get_user_model()
        # Créer une structure par défaut si besoin
        structure, _ = Structure.objects.get_or_create(nom='Direction Générale', defaults={'description': 'Structure principale'})
        # Rôles
        admin_role = Role.objects.get(libelle='ADMIN')
        gestionnaire_role = Role.objects.get(libelle='GESTIONNAIRE')
        # Admin
        if not User.objects.filter(username='000001/A').exists():
            admin_user = User.objects.create_superuser(
                username='000001/A',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='Principal'
            )
            Agent.objects.create(
                matricule='000001/A',
                prenom='Admin',
                nom='Principal',
                date_naissance='1990-01-01',
                lieu_naissance='Ville',
                adresse='Adresse admin',
                email='admin@example.com',
                telephone='+221700000001',
                user=admin_user,
                structure=structure,
                role=admin_role,
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS('Superutilisateur admin créé (matricule: 000001/A, mdp: admin123)'))
        else:
            self.stdout.write('Admin déjà existant.')
        # Gestionnaire
        if not User.objects.filter(username='000002/G').exists():
            gest_user = User.objects.create_user(
                username='000002/G',
                email='gestionnaire@example.com',
                password='gestion123',
                first_name='Gestion',
                last_name='Naire'
            )
            Agent.objects.create(
                matricule='000002/G',
                prenom='Gestion',
                nom='Naire',
                date_naissance='1992-02-02',
                lieu_naissance='Ville',
                adresse='Adresse gestionnaire',
                email='gestionnaire@example.com',
                telephone='+221700000002',
                user=gest_user,
                structure=structure,
                role=gestionnaire_role,
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS('Gestionnaire créé (matricule: 000002/G, mdp: gestion123)'))
        else:
            self.stdout.write('Gestionnaire déjà existant.') 