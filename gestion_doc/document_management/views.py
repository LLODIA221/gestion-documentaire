from django.contrib import messages 
from django.shortcuts import get_object_or_404, redirect, render
from .models import CategorieDocument, Delegation, Permission, Role, Structure, Agent, Document, DocumentVersion, Journal, Demande
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required
import random
import string
from django.contrib.auth.hashers import make_password
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from django.core.paginator import Paginator
# Create your views here.

@login_required
def home(request):
    # Récupérer l'agent lié à l'utilisateur
    agent = getattr(request.user, 'agent_profile', None)
    role = getattr(agent, 'role', None)
    permissions = set()
    if role:
        permissions = set(role.permissions.values_list('entity', 'action'))

    # Définir les droits d'affichage pour chaque section
    def has_perm(entity, action='READ'):
        return (entity, action) in permissions or (entity, 'ALL') in permissions

    context = {
        'nb_delegations': Delegation.objects.count() if has_perm('DELEGATION') else None,
        'nb_structures': Structure.objects.count() if has_perm('STRUCTURE') else None,
        'nb_agents': Agent.objects.count() if has_perm('AGENTS') else None,
        'nb_documents': Document.objects.count() if has_perm('DOCUMENTS') else None,
        'nb_roles': Role.objects.count() if has_perm('ROLES') else None,
        'nb_categories': CategorieDocument.objects.count() if has_perm('CATEGORIE_DOCUMENTS') else None,
        'afficher_delegations': has_perm('DELEGATION'),
        'afficher_structures': has_perm('STRUCTURE'),
        'afficher_agents': has_perm('AGENTS'),
        'afficher_documents': has_perm('DOCUMENTS'),
        'afficher_roles': has_perm('ROLES'),
        'afficher_categories': has_perm('CATEGORIE_DOCUMENTS'),
    }
    # Ajout du contexte du context processor pour garantir la présence des variables afficher_*
    from document_management.context_processors import permissions_context
    context.update(permissions_context(request))
    return render(request, 'home.html', context)

#urls des structures
@login_required
def liste_structures(request):
    Structures = Structure.objects.all()
    paginator = Paginator(Structures, 10)  # nombre de structure par page
    page_number = request.GET.get('page')
    Structures = paginator.get_page(page_number)  # renvoie un objet Page
    log_event(request.user, 'READ', 'Structure', None, details="Consultation de la liste des structures", request=request)
    return render(request, 'structures/liste.html', {'structures': Structures})

# Fonction utilitaire pour journaliser

def log_event(user, action, model_name, object_id, details=None, request=None):
    ip = None
    if request is not None:
        ip = request.META.get('REMOTE_ADDR')
    Journal.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=str(object_id) if object_id else '',
        details=details or '',
        ip_address=ip,
        timestamp=timezone.now()
    )

@login_required
def add_structure(request):
    delegations = Delegation.objects.all()
    if request.method == 'POST':
        nom = request.POST.get('nom')
        description = request.POST.get('description')
        delegation_id = request.POST.get('delegation')
        delegation = Delegation.objects.get(id=delegation_id) if delegation_id else None
        
        try:
            structure = Structure.objects.create(
                nom=nom,
                description=description,
                delegation=delegation
            )
            log_event(request.user, 'CREATE', 'Structure', structure.id, details=f"Ajout de la structure {nom}")
            messages.success(request, 'Structure ajoutée avec succès')
            return redirect('liste_structures')
        except Exception as e:
            messages.error(request, 'Une erreur est survenue lors de la création de la structure. Vérifiez que le nom n\'existe pas déjà.')
            return render(request, 'structures/form.html', {
                'delegations': delegations,
                'nom': nom,
                'description': description,
                'delegation_id': delegation_id
            })
    return render(request, 'structures/form.html', {
        'delegations': delegations
    })

@login_required
def update_structure(request, structure_id):
    structure = Structure.objects.get(id=structure_id)
    delegations = Delegation.objects.all()
    if request.method == 'POST':
        old_nom = structure.nom
        try:
            structure.nom = request.POST.get('nom')
            structure.description = request.POST.get('description')
            delegation_id = request.POST.get('delegation')
            structure.delegation = Delegation.objects.get(id=delegation_id) if delegation_id else None
            structure.save()
            log_event(request.user, 'UPDATE', 'Structure', structure.id, details=f"Modification de la structure {old_nom} -> {structure.nom}")
            messages.success(request, 'Structure modifiée avec succès')
            return redirect('liste_structures')
        except Exception as e:
            messages.error(request, 'Une erreur est survenue lors de la modification de la structure. Vérifiez que le nom n\'existe pas déjà.')
            return render(request, 'structures/form.html', {
                'structure': structure,
                'delegations': delegations
            })
    return render(request, 'structures/form.html', {
        'structure': structure,
        'delegations': delegations
    })

def delete_structure(request, structure_id):
    structure = get_object_or_404(Structure, id=structure_id)
    if request.method == 'POST':
        log_event(request.user, 'DELETE', 'Structure', structure.id, details=f"Suppression de la structure {structure.nom}")
        structure.delete()
        return redirect('liste_structures')
    return render(request, 'structures/delete.html', {'structure': structure})  


@login_required
def detail_structure(request, structure_id):
    structure = get_object_or_404(Structure, id=structure_id)
    log_event(request.user, 'READ', 'Structure', structure.id, details=f"Consultation de la structure {structure.nom}", request=request)
    return render(request, 'structures/detail.html', {'structure': structure})


# urls des delegations
@login_required
def liste_delegations(request):
    delegations = Delegation.objects.all()
    paginator = Paginator(delegations, 10)  # nombre de délégation par page
    page_number = request.GET.get('page')
    delegations = paginator.get_page(page_number)  # renvoie un objet Page
    log_event(request.user, 'READ', 'Delegation', None, details="Consultation de la liste des délégations", request=request)
    return render(request, 'delegations/liste.html', {'delegations': delegations})

@login_required
def add_delegation(request):
    if request.method == 'POST':
        nom_delegation = request.POST.get('nom_delegation')
        localisation = request.POST.get('localisation')
        description = request.POST.get('description')
        
        try:
            delegation = Delegation.objects.create(
                nom_delegation=nom_delegation,
                localisation=localisation,
                description=description
            )
            log_event(request.user, 'CREATE', 'Delegation', delegation.id, details=f"Ajout de la délégation {nom_delegation}")
            messages.success(request, 'Délégation ajoutée avec succès')
            return redirect('liste_delegations')
        except Exception as e:
            messages.error(request, 'Une erreur est survenue lors de la création de la délégation. Vérifiez que le nom n\'existe pas déjà.')
            return render(request, 'delegations/form.html', {
                'nom_delegation': nom_delegation,
                'localisation': localisation,
                'description': description
            })
    return render(request, 'delegations/form.html')

@login_required
def update_delegation(request, delegation_id):
    delegation = Delegation.objects.get(id=delegation_id)
    if request.method == 'POST':
        old_nom = delegation.nom_delegation
        try:
            delegation.nom_delegation = request.POST.get('nom_delegation')
            delegation.localisation = request.POST.get('localisation')
            delegation.description = request.POST.get('description')
            delegation.save()
            log_event(request.user, 'UPDATE', 'Delegation', delegation.id, details=f"Modification de la délégation {old_nom} -> {delegation.nom_delegation}")
            messages.success(request, 'Délégation modifiée avec succès')
            return redirect('liste_delegations')
        except Exception as e:
            messages.error(request, 'Une erreur est survenue lors de la modification de la délégation. Vérifiez que le nom n\'existe pas déjà.')
            return render(request, 'delegations/form.html', {
                'delegation': delegation
            })
    return render(request, 'delegations/form.html', {'delegation': delegation})

def delete_delegation(request, delegation_id):
    delegation = get_object_or_404(Delegation, id=delegation_id)
    if request.method == 'POST':
        log_event(request.user, 'DELETE', 'Delegation', delegation.id, details=f"Suppression de la délégation {delegation.nom_delegation}")
        delegation.delete()
        return redirect('liste_delegations')
    return render(request, 'delegations/delete.html', {'delegation': delegation})

@login_required
def detail_delegation(request, delegation_id):
    delegation = get_object_or_404(Delegation, id=delegation_id)
    log_event(request.user, 'READ', 'Delegation', delegation.id, details=f"Consultation de la délégation {delegation.nom_delegation}", request=request)
    return render(request, 'delegations/detail.html', {'delegation': delegation})


#urls des categories

@login_required
def liste_CategorieDocuments(request):
    """Affiche la liste des catégories de documents."""
    categoriesDocuments = CategorieDocument.objects.all()  
    paginator = Paginator(categoriesDocuments, 10)  # nombre de catégorie par page
    page_number = request.GET.get('page')
    categoriesDocuments = paginator.get_page(page_number)  # renvoie un objet Page
    log_event(request.user, 'READ', 'CategorieDocument', None, details="Consultation de la liste des catégories", request=request)
    return render(request, 'CategorieDocuments/liste.html', {'categoriesDocuments': categoriesDocuments})

@login_required
def add_categorieDocument(request):
    type_acces_choices = dict(CategorieDocument.TYPE_ACCES_CHOICES)
    if request.method == 'POST':
        libelle = request.POST.get('libelle')
        type_acces = request.POST.get('type_acces')
        description = request.POST.get('description')
        
        try:
            categorie = CategorieDocument.objects.create(
                libelle=libelle,
                type_acces=type_acces,
                description=description
            )
            log_event(request.user, 'CREATE', 'CategorieDocument', categorie.id, details=f"Ajout de la catégorie {libelle}")
            messages.success(request, 'Catégorie ajoutée avec succès')
            return redirect('liste_CategorieDocuments')
        except Exception as e:
            messages.error(request, 'Une erreur est survenue lors de la création de la catégorie. Vérifiez que le libellé n\'existe pas déjà.')
            return render(request, 'CategorieDocuments/form.html', {
                'type_acces_choices': type_acces_choices,
                'libelle': libelle,
                'type_acces': type_acces,
                'description': description
            })
    return render(request, 'CategorieDocuments/form.html', {
        'type_acces_choices': type_acces_choices
    })

@login_required
def update_categorieDocument(request, categorieDocument_id):
    categorieDocument = get_object_or_404(CategorieDocument, id=categorieDocument_id)
    type_acces_choices = dict(CategorieDocument.TYPE_ACCES_CHOICES)
    if request.method == 'POST':
        old_libelle = categorieDocument.libelle
        try:
            categorieDocument.libelle = request.POST.get('libelle')
            categorieDocument.type_acces = request.POST.get('type_acces')
            categorieDocument.description = request.POST.get('description')
            categorieDocument.save()
            log_event(request.user, 'UPDATE', 'CategorieDocument', categorieDocument.id, details=f"Modification de la catégorie {old_libelle} -> {categorieDocument.libelle}")
            messages.success(request, 'Catégorie modifiée avec succès')
            return redirect('liste_CategorieDocuments')
        except Exception as e:
            messages.error(request, 'Une erreur est survenue lors de la modification de la catégorie. Vérifiez que le libellé n\'existe pas déjà.')
            return render(request, 'CategorieDocuments/form.html', {
                'categorieDocument': categorieDocument,
                'type_acces_choices': type_acces_choices
            })
    return render(request, 'CategorieDocuments/form.html', {
        'categorieDocument': categorieDocument,
        'type_acces_choices': type_acces_choices
    })

def delete_categorieDocument(request, categorieDocument_id):
    categorieDocument = get_object_or_404(CategorieDocument, id=categorieDocument_id)
    if request.method == 'POST':
        log_event(request.user, 'DELETE', 'CategorieDocument', categorieDocument.id, details=f"Suppression de la catégorie {categorieDocument.libelle}")
        categorieDocument.delete()
        return redirect('liste_CategorieDocuments')
    return render(request, 'CategorieDocuments/delete.html', {'categorieDocument': categorieDocument})

@login_required
def detail_categorieDocument(request, categorieDocument_id):
    """Affiche les détails d'une catégorie de document."""
    categorieDocument = get_object_or_404(CategorieDocument, id=categorieDocument_id)
    log_event(request.user, 'READ', 'CategorieDocument', categorieDocument.id, details=f"Consultation de la catégorie {categorieDocument.libelle}", request=request)
    return render(request, 'CategorieDocuments/detail.html', {'categorieDocument': categorieDocument})

# Vues pour les permissions

@login_required
def liste_permissions(request):
    permissions_list = Permission.objects.all().order_by('entity', 'action')
    paginator = Paginator(permissions_list, 10)  # nombre de permissions par page

    page_number = request.GET.get('page')
    permissions = paginator.get_page(page_number)  # renvoie un objet Page

    # Logging
    log_event(request.user, 'READ', 'Permission', None, details="Consultation de la liste des permissions", request=request)

    return render(request, 'permissions/liste.html', {
        'permissions': permissions
    })


@login_required
def add_permission(request):
    if request.method == 'POST':
        entity = request.POST.get('entity')
        action = request.POST.get('action')
        description = request.POST.get('description', '')
        if Permission.objects.filter(entity=entity, action=action).exists():
            messages.error(request, "Cette permission existe déjà.")
            return render(request, 'permissions/form.html', {
                'permission_form': Permission,
                'permission': None,
            })
        permission = Permission.objects.create(
            entity=entity,
            action=action,
            description=description
        )
        log_event(request.user, 'CREATE', 'Permission', permission.id, details=f"Ajout de la permission {entity} {action}")
        messages.success(request, "Permission ajoutée avec succès")
        return redirect('liste_permissions')

    return render(request, 'permissions/form.html', {
        'permission_form': Permission,
        'permission': None
    })

@login_required
def update_permission(request, permission_id):
    permission = get_object_or_404(Permission, id=permission_id)
    if request.method == 'POST':
        old_entity = permission.entity
        old_action = permission.action
        entity = request.POST.get('entity')
        action = request.POST.get('action')
        description = request.POST.get('description', '')
        if Permission.objects.exclude(id=permission.id).filter(entity=entity, action=action).exists():
            messages.error(request, "Cette permission existe déjà.")
            return render(request, 'permissions/form.html', {
                'permission_form': Permission,
                'permission': permission
            })
        permission.entity = entity
        permission.action = action
        permission.description = description
        permission.save()
        log_event(request.user, 'UPDATE', 'Permission', permission.id, details=f"Modification de la permission {old_entity} {old_action} -> {entity} {action}")
        messages.success(request, "Permission modifiée avec succès")
        return redirect('liste_permissions')



@login_required
def delete_permission(request, permission_id):
    permission = get_object_or_404(Permission, id=permission_id)
    if request.method == 'POST':
        log_event(request.user, 'DELETE', 'Permission', permission.id, details=f"Suppression de la permission {permission.entity} {permission.action}")
        permission.delete()
        messages.success(request, "Permission supprimée avec succès")
        return redirect('liste_permissions')

    return render(request, 'permissions/delete.html', {'permission': permission})

@login_required
def detail_permission(request, permission_id):
    permission = get_object_or_404(Permission, id=permission_id)
    log_event(request.user, 'READ', 'Permission', permission.id, details=f"Consultation de la permission {permission.entity} {permission.action}", request=request)
    return render(request, 'permissions/detail.html', {'permission': permission})

# Vues pour les rôles
@login_required
def liste_roles(request):
    roles = Role.objects.all()
    paginator = Paginator(roles, 10)  # nombre de role par page
    page_number = request.GET.get('page')
    roles = paginator.get_page(page_number)  # renvoie un objet Page
    log_event(request.user, 'READ', 'Role', None, details="Consultation de la liste des rôles", request=request)
    return render(request, 'roles/liste.html', {'roles': roles})

@login_required
def add_role(request):
    permissions = Permission.objects.all()
    # Grouper les permissions par entité puis par action
    grouped_permissions = {}
    for entity, entity_label in Permission.ENTITY_CHOICES:
        grouped_permissions[entity] = {
            'label': entity_label,
            'actions': {}
        }
    for perm in permissions:
        if perm.entity in grouped_permissions:
            grouped_permissions[perm.entity]['actions'][perm.action] = perm
    if request.method == 'POST':
        libelle = request.POST.get('libelle')
        description = request.POST.get('description')
        selected_permissions = request.POST.getlist('permissions')
        role = Role(
            libelle=libelle,
            description=description,
        )
        role.save()  
        role.permissions.set(selected_permissions)
        log_event(request.user, 'CREATE', 'Role', role.id, details=f"Ajout du rôle {libelle}")
        messages.success(request, "Rôle ajouté avec succès")
        return redirect('liste_roles')

    return render(request, 'roles/form.html', {
        'grouped_permissions': grouped_permissions,
        'permissions': permissions,  # pour compatibilité éventuelle
        'role_choices': dict(Role.ROLE_CHOICES),
    })


@login_required
def update_role(request, role_id):
    role = get_object_or_404(Role, id=role_id)
    permissions = Permission.objects.all()
    # Grouper les permissions par entité puis par action
    grouped_permissions = {}
    for entity, entity_label in Permission.ENTITY_CHOICES:
        grouped_permissions[entity] = {
            'label': entity_label,
            'actions': {}
        }
    for perm in permissions:
        if perm.entity in grouped_permissions:
            grouped_permissions[perm.entity]['actions'][perm.action] = perm
    if request.method == 'POST':
        old_libelle = role.libelle
        role.libelle = request.POST.get('libelle')
        role.description = request.POST.get('description')
        role.save()
        selected_permissions = request.POST.getlist('permissions')
        role.permissions.set(selected_permissions)
        log_event(request.user, 'UPDATE', 'Role', role.id, details=f"Modification du rôle {old_libelle} -> {role.libelle}")
        messages.success(request, "Rôle mis à jour avec succès")
        return redirect('liste_roles')

    return render(request, 'roles/form.html', {
        'role': role,
        'grouped_permissions': grouped_permissions,
        'permissions': permissions,  # pour compatibilité éventuelle
        'role_choices': dict(Role.ROLE_CHOICES),
    })


@login_required
def delete_role(request, role_id):
    role = get_object_or_404(Role, id=role_id)
    if request.method == 'POST':
        log_event(request.user, 'DELETE', 'Role', role.id, details=f"Suppression du rôle {role.libelle}")
        role.delete()
        messages.success(request, "Rôle supprimé avec succès")
        return redirect('liste_roles')

    return render(request, 'roles/delete.html', {'role': role})

@login_required
def detail_role(request, role_id):
    role = get_object_or_404(Role, id=role_id)
    log_event(request.user, 'READ', 'Role', role.id, details=f"Consultation du rôle {role.libelle}", request=request)
    return render(request, 'roles/detail.html', {'role': role})

# Vues pour les agents
User = get_user_model()

@login_required
def liste_agents(request):
    agents = Agent.objects.all()
    paginator = Paginator(agents, 10)  # nombre de agent par page
    page_number = request.GET.get('page')
    agents = paginator.get_page(page_number)  # renvoie un objet Page
    log_event(request.user, 'READ', 'Agent', None, details="Consultation de la liste des agents", request=request)
    return render(request, 'agents/liste.html', {'agents': agents})

@login_required
def add_agent(request):
    structures = Structure.objects.all()
    roles = Role.objects.all()
    if request.method == 'POST':
        matricule = request.POST.get('matricule')
        prenom = request.POST.get('prenom')
        nom = request.POST.get('nom')
        date_naissance = request.POST.get('date_naissance')
        lieu_naissance = request.POST.get('lieu_naissance')
        adresse = request.POST.get('adresse')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        structure_id = request.POST.get('structure')
        role_id = request.POST.get('role')
        is_active = request.POST.get('is_active') == 'on'
        photo = request.FILES.get('photo')
        
        if Agent.objects.filter(matricule=matricule).exists():
            messages.error(request, "Ce matricule est déjà utilisé.")
        elif Agent.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
        elif Agent.objects.filter(telephone=telephone).exists():
            messages.error(request, "Ce numéro de téléphone est déjà utilisé.")
        else:
            try:
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                user = User.objects.create_user(
                    username=matricule,
                    email=email,
                    password=password,
                    first_name=prenom,
                    last_name=nom
                )
                role = Role.objects.get(id=role_id)
                agent = Agent.objects.create(
                    matricule=matricule,
                    prenom=prenom,
                    nom=nom,
                    date_naissance=date_naissance,
                    lieu_naissance=lieu_naissance,
                    adresse=adresse,
                    email=email,
                    telephone=telephone,
                    user=user,
                    structure=Structure.objects.get(id=structure_id),
                    role=role,
                    is_active=is_active,
                    photo=photo
                )
                log_event(request.user, 'CREATE', 'Agent', agent.id, details=f"Ajout de l'agent {prenom} {nom}")
                messages.success(request, f"Agent ajouté avec succès. Identifiant : {user.username} | Mot de passe : {password}")
                return redirect('liste_agents')
            except Exception as e:
                messages.error(request, f"Erreur lors de l'ajout de l'agent : {e}")
    return render(request, 'agents/form.html', {
        'structures': structures,
        'roles': roles
    })

@login_required
def update_agent(request, agent_id):
    agent = get_object_or_404(Agent, id=agent_id)
    structures = Structure.objects.all()
    roles = Role.objects.all()
    if request.method == 'POST':
        old_nom = agent.nom
        agent.matricule = request.POST.get('matricule')
        agent.prenom = request.POST.get('prenom')
        agent.nom = request.POST.get('nom')
        agent.date_naissance = request.POST.get('date_naissance')
        agent.lieu_naissance = request.POST.get('lieu_naissance')
        agent.adresse = request.POST.get('adresse')
        agent.email = request.POST.get('email')
        agent.telephone = request.POST.get('telephone')
        structure_id = request.POST.get('structure')
        role_id = request.POST.get('role')
        agent.is_active = request.POST.get('is_active') == 'on'
        
        # Gestion de la photo
        if 'photo' in request.FILES:
            # Supprimer l'ancienne photo si elle existe
            if agent.photo:
                agent.photo.delete()
            agent.photo = request.FILES['photo']
            
        try:
            agent.structure = Structure.objects.get(id=structure_id)
            agent.role = Role.objects.get(id=role_id)
            agent.save()
            log_event(request.user, 'UPDATE', 'Agent', agent.id, details=f"Modification de l'agent {old_nom} -> {agent.nom}")
            messages.success(request, "Agent modifié avec succès")
            return redirect('liste_agents')
        except Exception as e:
            messages.error(request, f"Erreur lors de la modification de l'agent : {e}")
    return render(request, 'agents/form.html', {
        'agent': agent,
        'structures': structures,
        'roles': roles
    })

def delete_agent(request, agent_id):
    agent = get_object_or_404(Agent, id=agent_id)
    if request.method == 'POST':
        log_event(request.user, 'DELETE', 'Agent', agent.id, details=f"Suppression de l'agent {agent.nom}")
        agent.delete()
        messages.success(request, "Agent supprimé avec succès")
        return redirect('liste_agents')
    return render(request, 'agents/delete.html', {'agent': agent})

@login_required
def detail_agent(request, agent_id):
    agent = get_object_or_404(Agent, id=agent_id)
    log_event(request.user, 'READ', 'Agent', agent.id, details=f"Consultation de l'agent {agent.nom}", request=request)
    return render(request, 'agents/detail.html', {'agent': agent})

def liste_users(request):
    users = User.objects.all()
    paginator = Paginator(users, 10)  # nombre de user par page
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)  # renvoie un objet Page
    log_event(request.user, 'READ', 'User', None, details="Consultation de la liste des utilisateurs", request=request)
    return render(request, 'users/liste.html', {'users': users})

@login_required
def detail_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    log_event(request.user, 'READ', 'User', user.id, details=f"Consultation de l'utilisateur {user.username}", request=request)
    return render(request, 'users/detail.html', {'user': user})

def update_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.is_active = request.POST.get('is_active') == 'on'
        user.save()
        messages.success(request, "Utilisateur modifié avec succès")
        return redirect('liste_users')
    return render(request, 'users/form.html', {'user': user})

def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, "Utilisateur supprimé avec succès")
        return redirect('liste_users')
    return render(request, 'users/delete.html', {'user': user})

def reset_password_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    import random, string
    new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    if request.method == 'POST':
        user.set_password(new_password)
        user.save()
        messages.success(request, f"Mot de passe réinitialisé : {new_password}")
        return redirect('detail_user', user_id=user.id)
    return render(request, 'users/reset_password.html', {'user': user, 'new_password': new_password})

@login_required
def liste_documents(request):
    agent = getattr(request.user, 'agent_profile', None)
    role = getattr(agent, 'role', None)
    role_name = getattr(role, 'libelle', None)

    if role_name == 'AGENT':
        documents = Document.objects.filter(agent=agent)
    else:
        documents = Document.objects.all()
    paginator = Paginator(documents, 10)  # nombre de document par page
    page_number = request.GET.get('page')
    documents = paginator.get_page(page_number)  # renvoie un objet Page
    log_event(request.user, 'READ', 'Document', None, details="Consultation de la liste des documents", request=request)
    return render(request, 'documents/liste.html', {'documents': documents})

@login_required
def add_document(request):
    categories = CategorieDocument.objects.all()
    agents = Agent.objects.all()
    if request.method == 'POST':
        libelle = request.POST.get('libelle')
        date_expiration = request.POST.get('date_expiration')
        categorie_id = request.POST.get('categorie_document')
        agent_id = request.POST.get('agent')
        fichier = request.FILES.get('fichier')
        type_doc = None
        if fichier:
            ext = fichier.name.split('.')[-1].lower()
            if ext in ['pdf', 'jpeg', 'jpg', 'png', 'docx', 'xlsx']:
                if ext == 'jpg':
                    type_doc = 'JPEG'
                else:
                    type_doc = ext.upper()
        try:
            document = Document.objects.create(
                libelle=libelle,
                type=type_doc,
                date_expiration=date_expiration if date_expiration else None,
                categorie_document=CategorieDocument.objects.get(id=categorie_id),
                agent=Agent.objects.get(id=agent_id),
                fichier=fichier
            )
            log_event(request.user, 'CREATE', 'Document', document.id, details=f"Ajout du document {libelle}")
            messages.success(request, "Document ajouté avec succès")
            return redirect('liste_documents')
        except Exception as e:
            messages.error(request, f"Erreur lors de l'ajout du document : {e}")
    return render(request, 'documents/form.html', {
        'categories': categories,
        'agents': agents
    })

@login_required
def update_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    categories = CategorieDocument.objects.all()
    agents = Agent.objects.all()
    if request.method == 'POST':
        old_libelle = document.libelle
        document.libelle = request.POST.get('libelle')
        document.date_expiration = request.POST.get('date_expiration') or None
        categorie_id = request.POST.get('categorie_document')
        agent_id = request.POST.get('agent')
        document.categorie_document = CategorieDocument.objects.get(id=categorie_id)
        document.agent = Agent.objects.get(id=agent_id)
        if request.FILES.get('fichier'):
            fichier = request.FILES.get('fichier')
            ext = fichier.name.split('.')[-1].lower()
            if ext in ['pdf', 'jpeg', 'jpg', 'png', 'docx', 'xlsx']:
                if ext == 'jpg':
                    document.type = 'JPEG'
                else:
                    document.type = ext.upper()
            document.fichier = fichier
        try:
            document.save()
            log_event(request.user, 'UPDATE', 'Document', document.id, details=f"Modification du document {old_libelle} -> {document.libelle}")
            messages.success(request, "Document modifié avec succès")
            return redirect('liste_documents')
        except Exception as e:
            messages.error(request, f"Erreur lors de la modification du document : {e}")
    return render(request, 'documents/form.html', {
        'document': document,
        'categories': categories,
        'agents': agents
    })

def delete_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    if request.method == 'POST':
        log_event(request.user, 'DELETE', 'Document', document.id, details=f"Suppression du document {document.libelle}")
        document.delete()
        messages.success(request, "Document supprimé avec succès")
        return redirect('liste_documents')
    return render(request, 'documents/delete.html', {'document': document})

def add_document_version(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    if request.method == 'POST':
        fichier = request.FILES.get('fichier')
        change_summary = request.POST.get('change_summary', '')
        type_doc = None
        if fichier:
            ext = fichier.name.split('.')[-1].lower()
            if ext in ['pdf', 'jpeg', 'jpg', 'png', 'docx', 'xlsx']:
                if ext == 'jpg':
                    type_doc = 'JPEG'
                else:
                    type_doc = ext.upper()
        DocumentVersion.objects.create(
            document=document,
            fichier=fichier,
            type=type_doc,
            change_summary=change_summary,
            created_by=request.user
        )
        # Optionnel : mettre à jour le fichier principal du document
        document.fichier = fichier
        document.type = type_doc
        document.save()
        messages.success(request, "Nouvelle version ajoutée avec succès.")
        return redirect('detail_document', document_id=document.id)
    return render(request, 'documents/version_form.html', {'document': document})

@login_required
def detail_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    versions = document.versions.order_by('-version_number')
    log_event(request.user, 'READ', 'Document', document.id, details=f"Consultation du document {document.libelle}", request=request)
    return render(request, 'documents/detail.html', {'document': document, 'versions': versions})

def custom_login_view(request):
    if request.method == 'POST':
        matricule = request.POST['matricule']
        password = request.POST['password']
        user = authenticate(request, username=matricule, password=password)
        if user is not None:
            login(request, user)
            log_event(user, 'LOGIN', 'User', user.id, details=f"Connexion de {user.username}", request=request)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Identifiants invalides'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# Vue pour la liste des journaux
@login_required
def liste_journaux(request):
    journaux = Journal.objects.select_related('user').order_by('-timestamp')[:200]
    paginator = Paginator(journaux, 10)  # 10 journaux par page
    page_number = request.GET.get('page')
    journaux = paginator.get_page(page_number)
    return render(request, 'journaux/liste.html', {'journaux': journaux})


# Vue pour le détail d'un journal
@login_required
def detail_journal(request, journal_id):
    journal = get_object_or_404(Journal, id=journal_id)
    return render(request, 'journaux/detail.html', {'journal': journal})

@login_required
def profile(request):
    """
    Vue pour afficher le profil de l'utilisateur connecté
    """
    agent = request.user.agent_profile
    nb_documents_agent = Document.objects.filter(agent=agent).count()
    nb_demandes_agent = Demande.objects.filter(demandeur=request.user).count()
    
    return render(request, 'profile.html', {
        'nb_documents_agent': nb_documents_agent,
        'nb_demandes_agent': nb_demandes_agent,
    })