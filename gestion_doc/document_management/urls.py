from django.urls import path
from  .views import *


urlpatterns = [

    path('',home,name='home'),
    path('structure/', liste_structures, name='liste_structures'),
    path('structure/add/', add_structure, name='add_structure'),
    path('structure/update/<int:structure_id>/', update_structure, name='update_structure'),
    path('structure/delete/<int:structure_id>/', delete_structure, name='delete_structure'),
    path('structure/detail/<int:structure_id>/', detail_structure, name='detail_structure'),
    
    # urls des delegations
    path('delegation/', liste_delegations, name='liste_delegations'),
    path('delegation/add/', add_delegation, name='add_delegation'),
    path('delegation/update/<int:delegation_id>/', update_delegation, name='update_delegation'),
    path('delegation/delete/<int:delegation_id>/', delete_delegation, name='delete_delegation'),
    path('delegation/detail/<int:delegation_id>/', detail_delegation, name='detail_delegation'),

    #urls des categories
    path('categorie/', liste_CategorieDocuments, name='liste_CategorieDocuments'),
    path('categorie/add/', add_categorieDocument, name='add_categorieDocument'),
    path('categorie/update/<int:categorieDocument_id>/', update_categorieDocument, name='update_categorieDocument'),
    path('categorie/delete/<int:categorieDocument_id>/', delete_categorieDocument, name='delete_categorieDocument'),
    path('categorie/detail/<int:categorieDocument_id>/', detail_categorieDocument, name='detail_categorieDocument'),

  # Permissions
    path('permissions/', liste_permissions, name='liste_permissions'),
    path('permissions/add/', add_permission, name='add_permission'),
    path('permissions/update/<int:permission_id>/', update_permission, name='update_permission'),
    path('permissions/delete/<int:permission_id>/', delete_permission, name='delete_permission'),
    path('permissions/detail/<int:permission_id>/', detail_permission, name='detail_permission'),

    # Rôles
    path('roles/', liste_roles, name='liste_roles'),
    path('roles/add/', add_role, name='add_role'),
    path('roles/update/<int:role_id>/', update_role, name='update_role'),
    path('roles/delete/<int:role_id>/', delete_role, name='delete_role'),
    path('roles/detail/<int:role_id>/', detail_role, name='detail_role'),

    # Agents
    path('agent/', liste_agents, name='liste_agents'),
    path('agent/add/', add_agent, name='add_agent'),
    path('agent/update/<int:agent_id>/', update_agent, name='update_agent'),
    path('agent/delete/<int:agent_id>/', delete_agent, name='delete_agent'),
    path('agent/detail/<int:agent_id>/', detail_agent, name='detail_agent'),

    # Utilisateurs
    path('users/', liste_users, name='liste_users'),
    path('users/<int:user_id>/', detail_user, name='detail_user'),
    path('users/update/<int:user_id>/', update_user, name='update_user'),
    path('users/delete/<int:user_id>/', delete_user, name='delete_user'),
    path('users/reset_password/<int:user_id>/', reset_password_user, name='reset_password_user'),

    # Documents
    path('documents/', liste_documents, name='liste_documents'),
    path('documents/add/', add_document, name='add_document'),
    path('documents/update/<int:document_id>/', update_document, name='update_document'),
    path('documents/delete/<int:document_id>/', delete_document, name='delete_document'),
    path('documents/detail/<int:document_id>/', detail_document, name='detail_document'),
    path('documents/<int:document_id>/add_version/', add_document_version, name='add_document_version'),

    path('login/', custom_login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]