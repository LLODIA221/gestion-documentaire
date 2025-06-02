from .models import Document

def permissions_context(request):
    user = request.user
    agent = getattr(user, 'agent_profile', None)
    role = getattr(agent, 'role', None)
    role_name = getattr(role, 'libelle', None)

    # Par défaut, tout est caché
    afficher_delegations = afficher_structures = afficher_agents = afficher_documents = afficher_roles = afficher_categories = afficher_users = afficher_permissions = afficher_notifications = afficher_demandes = False

    if role_name == 'ADMIN':
        afficher_delegations = afficher_structures = afficher_agents = afficher_documents = afficher_roles = afficher_categories = afficher_users = afficher_permissions = afficher_notifications = afficher_demandes = True
    elif role_name == 'GESTIONNAIRE':
        afficher_delegations = afficher_structures = afficher_agents = afficher_documents = afficher_roles = afficher_categories = afficher_permissions = afficher_notifications = afficher_demandes = True
        afficher_users = False
    elif role_name == 'CONTROLLER':
        afficher_agents = afficher_documents = afficher_categories = afficher_structures = afficher_roles = afficher_permissions = afficher_users = afficher_notifications = afficher_demandes = True
        # Lecture seule, pas de création/modif/suppression
    elif role_name == 'AGENT':
        afficher_documents = afficher_notifications = afficher_demandes = True
    else:
        pass  # Aucun accès

    # Pour l'agent, nombre de documents propres
    nb_documents_agent = Document.objects.filter(agent=agent).count() if agent and role_name == 'AGENT' else None

    return {
        'afficher_delegations': afficher_delegations,
        'afficher_structures': afficher_structures,
        'afficher_agents': afficher_agents,
        'afficher_documents': afficher_documents,
        'afficher_roles': afficher_roles,
        'afficher_categories': afficher_categories,
        'afficher_users': afficher_users,
        'afficher_permissions': afficher_permissions,
        'afficher_notifications': afficher_notifications,
        'afficher_demandes': afficher_demandes,
        'nb_documents_agent': nb_documents_agent,
        'role_name': role_name,
    } 