from .models import Document, Delegation, Structure, Agent, Role, CategorieDocument

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
        afficher_agents = afficher_documents = afficher_categories = afficher_structures = afficher_delegations = afficher_roles = afficher_permissions = afficher_users = afficher_notifications = afficher_demandes = True
        # Lecture seule, pas de création/modif/suppression
    elif role_name == 'AGENT':
        afficher_documents = afficher_notifications = afficher_demandes = True
    else:
        pass  # Aucun accès

    # Pour l'agent, nombre de documents propres
    nb_documents_agent = Document.objects.filter(agent=agent).count() #if agent and role_name == 'AGENT' else None

    # Compteurs globaux pour chaque entité
    nb_delegations = Delegation.objects.count()
    nb_structures = Structure.objects.count()
    nb_agents = Agent.objects.count()
    nb_documents = Document.objects.count()
    nb_roles = Role.objects.count()
    nb_categories = CategorieDocument.objects.count()

    # Permissions fines pour les templates
    # Initialiser toutes les variables de permissions à False par défaut
    can_read_documents = can_create_documents = can_update_documents = can_delete_documents = False
    can_read_agents = can_create_agents = can_update_agents = can_delete_agents = False
    can_read_roles = can_create_roles = can_update_roles = can_delete_roles = False
    can_read_structures = can_create_structures = can_update_structures = can_delete_structures = False
    can_read_delegations = can_create_delegations = can_update_delegations = can_delete_delegations = False
    can_read_categories = can_create_categories = can_update_categories = can_delete_categories = False
    can_read_permissions = can_create_permissions = can_update_permissions = can_delete_permissions = False
    can_read_users = can_create_users = can_update_users = can_delete_users = False

    if role_name == 'AGENT':
        can_read_documents = True
        can_read_notifications = True
        can_read_demandes = True
    else:
        permissions = set()
        if role:
            permissions = set(role.permissions.values_list('entity', 'action'))
        def has_perm(entity, action):
            return (entity, action) in permissions or (entity, 'ALL') in permissions
        
        can_read_documents = has_perm('DOCUMENTS', 'READ')
        can_create_documents = has_perm('DOCUMENTS', 'CREATE')
        can_update_documents = has_perm('DOCUMENTS', 'UPDATE')
        can_delete_documents = has_perm('DOCUMENTS', 'DELETE')
        can_read_agents = has_perm('AGENTS', 'READ')
        can_create_agents = has_perm('AGENTS', 'CREATE')
        can_update_agents = has_perm('AGENTS', 'UPDATE')
        can_delete_agents = has_perm('AGENTS', 'DELETE')
        can_read_roles = has_perm('ROLES', 'READ')
        can_create_roles = has_perm('ROLES', 'CREATE')
        can_update_roles = has_perm('ROLES', 'UPDATE')
        can_delete_roles = has_perm('ROLES', 'DELETE')
        can_read_permissions = has_perm('PERMISSIONS', 'READ')
        can_create_permissions = has_perm('PERMISSIONS', 'CREATE')
        can_update_permissions = has_perm('PERMISSIONS', 'UPDATE')
        can_delete_permissions = has_perm('PERMISSIONS', 'DELETE')
        can_read_structures = has_perm('STRUCTURE', 'READ')
        can_create_structures = has_perm('STRUCTURE', 'CREATE')
        can_update_structures = has_perm('STRUCTURE', 'UPDATE')
        can_delete_structures = has_perm('STRUCTURE', 'DELETE')
        can_read_delegations = has_perm('DELEGATION', 'READ')
        can_create_delegations = has_perm('DELEGATION', 'CREATE')
        can_update_delegations = has_perm('DELEGATION', 'UPDATE')
        can_delete_delegations = has_perm('DELEGATION', 'DELETE')
        can_read_categories = has_perm('CATEGORIE_DOCUMENTS', 'READ')
        can_create_categories = has_perm('CATEGORIE_DOCUMENTS', 'CREATE')
        can_update_categories = has_perm('CATEGORIE_DOCUMENTS', 'UPDATE')
        can_delete_categories = has_perm('CATEGORIE_DOCUMENTS', 'DELETE')
        #permissions pour les utilisateurs
        can_read_users = has_perm('USERS', 'READ')
        can_create_users = has_perm('USERS', 'CREATE')  
        can_update_users = has_perm('USERS', 'UPDATE')
        can_delete_users = has_perm('USERS', 'DELETE')

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
        'nb_delegations': nb_delegations,
        'nb_structures': nb_structures,
        'nb_agents': nb_agents,
        'nb_documents': nb_documents,
        'nb_roles': nb_roles,
        'nb_categories': nb_categories,
        # Permissions fines pour les templates
        'can_read_documents': can_read_documents,
        'can_create_documents': can_create_documents,
        'can_update_documents': can_update_documents,
        'can_delete_documents': can_delete_documents,
        'can_read_agents': can_read_agents,
        'can_create_agents': can_create_agents,
        'can_update_agents': can_update_agents,
        'can_delete_agents': can_delete_agents,
        'can_read_roles': can_read_roles,
        'can_create_roles': can_create_roles,
        'can_update_roles': can_update_roles,
        'can_delete_roles': can_delete_roles,
        'can_read_permissions': can_read_permissions,  # Seul l'admin peut lire les permissions
        'can_create_permissions': role_name == 'ADMIN',  # Seul l'admin peut créer des permissions
        'can_update_permissions': role_name == 'ADMIN',  # Seul l'admin peut mettre à jour les permissions
        'can_delete_permissions': role_name == 'ADMIN',  # Seul l'admin peut supprimer des permissions
        'can_read_users': can_read_users,
        'can_create_users': can_create_users,
        'can_update_users': can_update_users,
        'can_delete_users': can_delete_users,
        'can_read_structures': can_read_structures,
        'can_create_structures': can_create_structures,
        'can_update_structures': can_update_structures,
        'can_delete_structures': can_delete_structures,
        'can_read_delegations': can_read_delegations,
        'can_create_delegations': can_create_delegations,
        'can_update_delegations': can_update_delegations,
        'can_delete_delegations': can_delete_delegations,
        'can_read_categories': can_read_categories,
        'can_create_categories': can_create_categories,
        'can_update_categories': can_update_categories,
        'can_delete_categories': can_delete_categories,
    } 