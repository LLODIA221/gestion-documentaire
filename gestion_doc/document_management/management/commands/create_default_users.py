from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from ...models import Agent, Role, Structure, Permission


class Command(BaseCommand):
    help = 'Crée 4 utilisateurs par défaut pour les rôles ADMIN, GESTIONNAIRE, CONTROLLER, AGENT avec matricule 606620/...'

    def handle(self, *args, **options):
        User = get_user_model()
        # Créer une structure par défaut si besoin
        structure, _ = Structure.objects.get_or_create(nom='Direction Générale', defaults={'description': 'Structure principale'})
        # Créer les rôles s'ils n'existent pas
        role_defs = [
            ('ADMIN', 'Administrateur', 'Rôle administrateur'),
            ('GESTIONNAIRE', 'Gestionnaire', 'Rôle gestionnaire'),
            ('CONTROLLER', 'Contrôleur', 'Rôle contrôleur'),
            ('AGENT', 'Agent', 'Rôle agent'),
        ]
        for code, label, desc in role_defs:
            Role.objects.get_or_create(libelle=code, defaults={'description': desc})
        # Rôles
        admin_role = Role.objects.get(libelle='ADMIN')
        gestionnaire_role = Role.objects.get(libelle='GESTIONNAIRE')
        controller_role = Role.objects.get(libelle='CONTROLLER')
        agent_role = Role.objects.get(libelle='AGENT')

        # Après la création des rôles
        all_permissions = Permission.objects.all()
        admin_role.permissions.set(all_permissions)

        users_data = [
            {
                "role": admin_role,
                "matricule": "606620/A",
                "username": "606620/A",
                "email": "admin@example.com",
                "password": "admin123",
                "first_name": "Admin",
                "last_name": "Principal",
                "prenom": "Admin",
                "nom": "Principal",
                "date_naissance": "1990-01-01",
                "lieu_naissance": "Ville",
                "adresse": "Adresse admin",
                "telephone": "+221700000001",
                "is_superuser": True,
                "is_staff": True,
                "success_msg": "Superutilisateur admin créé (matricule: 606620/A, mdp: admin123)",
                "exist_msg": "Admin déjà existant."
            },
            {
                "role": gestionnaire_role,
                "matricule": "606620/B",
                "username": "606620/B",
                "email": "gestionnaire@example.com",
                "password": "gestion123",
                "first_name": "Gestion",
                "last_name": "Naire",
                "prenom": "Gestion",
                "nom": "Naire",
                "date_naissance": "1992-02-02",
                "lieu_naissance": "Ville",
                "adresse": "Adresse gestionnaire",
                "telephone": "+221700000002",
                "is_superuser": False,
                "is_staff": True,
                "success_msg": "Gestionnaire créé (matricule: 606620/B, mdp: gestion123)",
                "exist_msg": "Gestionnaire déjà existant."
            },
            {
                "role": controller_role,
                "matricule": "606620/C",
                "username": "606620/C",
                "email": "controleur@example.com",
                "password": "controle123",
                "first_name": "Controle",
                "last_name": "Heur",
                "prenom": "Controle",
                "nom": "Heur",
                "date_naissance": "1993-03-03",
                "lieu_naissance": "Ville",
                "adresse": "Adresse controleur",
                "telephone": "+221700000003",
                "is_superuser": False,
                "is_staff": True,
                "success_msg": "Contrôleur créé (matricule: 606620/C, mdp: controle123)",
                "exist_msg": "Contrôleur déjà existant."
            },
            {
                "role": agent_role,
                "matricule": "606620/D",
                "username": "606620/D",
                "email": "agent@example.com",
                "password": "agent123",
                "first_name": "Agent",
                "last_name": "Simple",
                "prenom": "Agent",
                "nom": "Simple",
                "date_naissance": "1994-04-04",
                "lieu_naissance": "Ville",
                "adresse": "Adresse agent",
                "telephone": "+221700000004",
                "is_superuser": False,
                "is_staff": False,
                "success_msg": "Agent créé (matricule: 606620/D, mdp: agent123)",
                "exist_msg": "Agent déjà existant."
            }
        ]

        for user_data in users_data:
            if not User.objects.filter(username=user_data["username"]).exists():
                if user_data["is_superuser"]:
                    user = User.objects.create_superuser(
                        username=user_data["username"],
                        email=user_data["email"],
                        password=user_data["password"],
                        first_name=user_data["first_name"],
                        last_name=user_data["last_name"]
                    )
                else:
                    user = User.objects.create_user(
                        username=user_data["username"],
                        email=user_data["email"],
                        password=user_data["password"],
                        first_name=user_data["first_name"],
                        last_name=user_data["last_name"]
                    )
                    if user_data["is_staff"]:
                        user.is_staff = True
                        user.save()
                Agent.objects.create(
                    matricule=user_data["matricule"],
                    prenom=user_data["prenom"],
                    nom=user_data["nom"],
                    date_naissance=user_data["date_naissance"],
                    lieu_naissance=user_data["lieu_naissance"],
                    adresse=user_data["adresse"],
                    email=user_data["email"],
                    telephone=user_data["telephone"],
                    user=user,
                    structure=structure,
                    role=user_data["role"],
                    is_active=True
                )
                self.stdout.write(self.style.SUCCESS(user_data["success_msg"]))
            else:
                self.stdout.write(user_data["exist_msg"])