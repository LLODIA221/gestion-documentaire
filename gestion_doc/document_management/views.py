from django.contrib import messages 
from django.shortcuts import get_object_or_404, redirect, render
from .models import CategorieDocument, Delegation, Permission, Role, Structure, Agent, Document, DocumentVersion
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required
import random
import string
from django.contrib.auth.hashers import make_password
from django.core.files.storage import FileSystemStorage
# Create your views here.

@login_required
def home(request):
    return render(request, 'home.html')

#urls des structures
@login_required
def liste_structures(request):
    Structures = Structure.objects.all() #liste de tous les structures
    return render(request, 'structures/liste.html', {'structures': Structures})

@login_required
def add_structure(request):
    # Récupérer la liste des délégations disponibles
    delegations = Delegation.objects.all()
    
    if request.method == 'POST':
        nom = request.POST.get('nom')
   
        description = request.POST.get('description')
        delegation_id = request.POST.get('delegation')
        
        delegation = Delegation.objects.get(id=delegation_id) if delegation_id else None

        Structure.objects.create(
            nom=nom,
        
            description=description,
            delegation=delegation
        )
        return redirect('liste_structures')
    return render(request, 'structures/form.html', {
        'message': 'Structure ajoutée avec succès',
        'delegations': delegations
    })

def update_structure(request, structure_id):
    structure = Structure.objects.get(id=structure_id)
    delegations = Delegation.objects.all()

    if request.method == 'POST':
        structure.nom = request.POST.get('nom')
        structure.description = request.POST.get('description')
        delegation_id = request.POST.get('delegation')
        structure.delegation = Delegation.objects.get(id=delegation_id) if delegation_id else None
        structure.save()
        return redirect('liste_structures')
    return render(request, 'structures/form.html', {
        'structure': structure,
        'delegations': delegations
    })

def delete_structure(request, structure_id):
    structure = get_object_or_404(Structure, id=structure_id)

    if request.method == 'POST':
        structure.delete()
        return redirect('liste_structures')

    return render(request, 'structures/delete.html', {'structure': structure})  


def detail_structure(request, structure_id):
    structure = get_object_or_404(Structure, id=structure_id)
    return render(request, 'structures/detail.html', {'structure': structure})


# urls des delegations
def liste_delegations(request):
    delegations = Delegation.objects.all() #liste de tous les delegations
    return render(request, 'delegations/liste.html', {'delegations': delegations})

def add_delegation(request):
    if request.method == 'POST':
        nom_delegation = request.POST.get('nom_delegation')
      
        localisation = request.POST.get('localisation')
      
        description = request.POST.get('description')

        Delegation.objects.create(

            nom_delegation=nom_delegation,
            localisation=localisation,
            description=description )
        return redirect('liste_delegations')
    return render(request, 'delegations/form.html', {'message': 'Delegation ajoutée avec succès'})

def update_delegation(request, delegation_id):
    delegation = Delegation.objects.get(id=delegation_id)
    if request.method == 'POST':
        delegation.nom_delegation = request.POST.get('nom_delegation')
      
        delegation.localisation = request.POST.get('localisation')
        delegation.description = request.POST.get('description')
      
        delegation.save()
        return redirect('liste_delegations')
    return render(request, 'delegations/form.html', {'delegation': delegation})

def delete_delegation(request, delegation_id):
    delegation = get_object_or_404(Delegation, id=delegation_id)

    if request.method == 'POST':
        delegation.delete()
        return redirect('liste_delegations')

    return render(request, 'delegations/delete.html', {'delegation': delegation})

def detail_delegation(request, delegation_id):
    delegation = get_object_or_404(Delegation, id=delegation_id)
    return render(request, 'delegations/detail.html', {'delegation': delegation})


#urls des categories

def liste_CategorieDocuments(request):
    """Affiche la liste des catégories de documents."""
    categoriesDocuments = CategorieDocument.objects.all()  
    return render(request, 'CategorieDocuments/liste.html', {'categoriesDocuments': categoriesDocuments})

def add_categorieDocument(request):
    """Ajoute une nouvelle catégorie de document."""
    type_acces_choices = dict(CategorieDocument.TYPE_ACCES_CHOICES)  # Récupérer les choix du modèle

    if request.method == 'POST':
        libelle = request.POST.get('libelle')
        type_acces = request.POST.get('type_acces')
        description = request.POST.get('description')

        CategorieDocument.objects.create(
            libelle=libelle,
            type_acces=type_acces,
            description=description
        )
        return redirect('liste_CategorieDocuments')

    return render(request, 'CategorieDocuments/form.html', {
        'type_acces_choices': type_acces_choices
    })

def update_categorieDocument(request, categorieDocument_id):
    """Met à jour une catégorie de document existante."""
    categorieDocument = get_object_or_404(CategorieDocument, id=categorieDocument_id)
    type_acces_choices = dict(CategorieDocument.TYPE_ACCES_CHOICES)

    if request.method == 'POST':
        categorieDocument.libelle = request.POST.get('libelle')
        categorieDocument.type_acces = request.POST.get('type_acces')
        categorieDocument.description = request.POST.get('description')

        categorieDocument.save()
        return redirect('liste_CategorieDocuments')

    return render(request, 'CategorieDocuments/form.html', {
        'categorieDocument': categorieDocument,
        'type_acces_choices': type_acces_choices
    })

def delete_categorieDocument(request, categorieDocument_id):
    """Supprime une catégorie de document."""
    categorieDocument = get_object_or_404(CategorieDocument, id=categorieDocument_id) 

    if request.method == 'POST':
        categorieDocument.delete()
        return redirect('liste_CategorieDocuments')

    return render(request, 'CategorieDocuments/delete.html', {'categorieDocument': categorieDocument})

def detail_categorieDocument(request, categorieDocument_id):
    """Affiche les détails d'une catégorie de document."""
    categorieDocument = get_object_or_404(CategorieDocument, id=categorieDocument_id)
    return render(request, 'CategorieDocuments/detail.html', {'categorieDocument': categorieDocument})

# Vues pour les permissions

def liste_permissions(request):
    permissions = Permission.objects.all()
    return render(request, 'permissions/liste.html', {'permissions': permissions})


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

        Permission.objects.create(
            entity=entity,
            action=action,
            description=description
        )
        messages.success(request, "Permission ajoutée avec succès")
        return redirect('liste_permissions')

    return render(request, 'permissions/form.html', {
        'permission_form': Permission,
        'permission': None
    })

def update_permission(request, permission_id):
    permission = get_object_or_404(Permission, id=permission_id)

    if request.method == 'POST':
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

        messages.success(request, "Permission modifiée avec succès")
        return redirect('liste_permissions')



def delete_permission(request, permission_id):
    permission = get_object_or_404(Permission, id=permission_id)
    if request.method == 'POST':
        permission.delete()
        messages.success(request, "Permission supprimée avec succès")
        return redirect('liste_permissions')

    return render(request, 'permissions/delete.html', {'permission': permission})

def detail_permission(request, permission_id):
    permission = get_object_or_404(Permission, id=permission_id)
    return render(request, 'permissions/detail.html', {'permission': permission})

# Vues pour les rôles
def liste_roles(request):
    roles = Role.objects.all()
    return render(request, 'roles/liste.html', {'roles': roles})

def add_role(request):
    permissions = Permission.objects.all()
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
        messages.success(request, "Rôle ajouté avec succès")
        return redirect('liste_roles')

    return render(request, 'roles/form.html', {
        'permissions': permissions,
        'role_choices': dict(Role.ROLE_CHOICES),
    })


def update_role(request, role_id):
    role = get_object_or_404(Role, id=role_id)
    permissions = Permission.objects.all()
    if request.method == 'POST':
        role.libelle = request.POST.get('libelle')
        role.description = request.POST.get('description')
        role.save()  # met à jour le niveau automatiquement
        selected_permissions = request.POST.getlist('permissions')
        role.permissions.set(selected_permissions)
        messages.success(request, "Rôle mis à jour avec succès")
        return redirect('liste_roles')

    return render(request, 'roles/form.html', {
        'role': role,
        'permissions': permissions,
        'role_choices': dict(Role.ROLE_CHOICES),
    })


def delete_role(request, role_id):
    role = get_object_or_404(Role, id=role_id)
    if request.method == 'POST':
        role.delete()
        messages.success(request, "Rôle supprimé avec succès")
        return redirect('liste_roles')

    return render(request, 'roles/delete.html', {'role': role})

def detail_role(request, role_id):
    role = get_object_or_404(Role, id=role_id)
    return render(request, 'roles/detail.html', {'role': role})

# Vues pour les agents
User = get_user_model()

def liste_agents(request):
    agents = Agent.objects.all()
    return render(request, 'agents/liste.html', {'agents': agents})

def add_agent(request):
    structures = Structure.objects.all()
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
        is_active = request.POST.get('is_active') == 'on'
        # Vérification unicité
        if Agent.objects.filter(matricule=matricule).exists():
            messages.error(request, "Ce matricule est déjà utilisé.")
        elif Agent.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
        elif Agent.objects.filter(telephone=telephone).exists():
            messages.error(request, "Ce numéro de téléphone est déjà utilisé.")
        else:
            try:
                # Générer un mot de passe aléatoire
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                # Créer l'utilisateur Django
                user = User.objects.create_user(
                    username=matricule,
                    email=email,
                    password=password,
                    first_name=prenom,
                    last_name=nom
                )
                # Récupérer le rôle "AGENT"
                role = Role.objects.get(libelle='AGENT')
                # Créer l'agent lié à ce user
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
                    is_active=is_active
                )
                messages.success(request, f"Agent ajouté avec succès. Identifiant : {user.username} | Mot de passe : {password}")
                return redirect('liste_agents')
            except Exception as e:
                messages.error(request, f"Erreur lors de l'ajout de l'agent : {e}")
    return render(request, 'agents/form.html', {
        'structures': structures
    })

def update_agent(request, agent_id):
    agent = get_object_or_404(Agent, id=agent_id)
    structures = Structure.objects.all()
    roles = Role.objects.all()
    if request.method == 'POST':
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
        try:
            agent.structure = Structure.objects.get(id=structure_id)
            agent.role = Role.objects.get(id=role_id)
            agent.save()
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
        agent.delete()
        messages.success(request, "Agent supprimé avec succès")
        return redirect('liste_agents')
    return render(request, 'agents/delete.html', {'agent': agent})

def detail_agent(request, agent_id):
    agent = get_object_or_404(Agent, id=agent_id)
    return render(request, 'agents/detail.html', {'agent': agent})

def liste_users(request):
    users = User.objects.all()
    return render(request, 'users/liste.html', {'users': users})

def detail_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
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

def liste_documents(request):
    documents = Document.objects.all()
    return render(request, 'documents/liste.html', {'documents': documents})

def add_document(request):
    categories = CategorieDocument.objects.all()
    agents = Agent.objects.all()
    if request.method == 'POST':
        libelle = request.POST.get('libelle')
        date_expiration = request.POST.get('date_expiration')
        categorie_id = request.POST.get('categorie_document')
        agent_id = request.POST.get('agent')
        fichier = request.FILES.get('fichier')
        # Déterminer le type à partir de l'extension
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
            messages.success(request, "Document ajouté avec succès")
            return redirect('liste_documents')
        except Exception as e:
            messages.error(request, f"Erreur lors de l'ajout du document : {e}")
    return render(request, 'documents/form.html', {
        'categories': categories,
        'agents': agents
    })

def update_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    categories = CategorieDocument.objects.all()
    agents = Agent.objects.all()
    if request.method == 'POST':
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

def detail_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    versions = document.versions.order_by('-version_number')
    return render(request, 'documents/detail.html', {'document': document, 'versions': versions})

def custom_login_view(request):
    if request.method == 'POST':
        matricule = request.POST['matricule']
        password = request.POST['password']
        user = authenticate(request, username=matricule, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # ou la page d'accueil de ton choix
        else:
            return render(request, 'login.html', {'error': 'Identifiants invalides'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')