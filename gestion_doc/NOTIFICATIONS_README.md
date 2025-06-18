# Système de Notifications - Gestion Documentaire

## Vue d'ensemble

Le système de notifications a été implémenté pour informer les utilisateurs des événements importants liés aux documents, notamment :
- **Expiration de documents** : Notifications automatiques pour les documents expirant bientôt ou déjà expirés
- **Création de documents** : Notifications lors de l'assignation de nouveaux documents
- **Modification de documents** : Notifications lors de la modification ou réassignation de documents

## Fonctionnalités

### 1. Notifications en temps réel
- Icône de cloche dans la navbar avec badge indiquant le nombre de notifications non lues
- Dropdown avec les 5 dernières notifications non lues
- Actualisation automatique toutes les 30 secondes
- Possibilité de marquer une notification comme lue en cliquant dessus

### 2. Page de gestion des notifications
- Liste complète de toutes les notifications de l'utilisateur
- Pagination (20 notifications par page)
- Filtrage par type (Information, Succès, Avertissement, Erreur)
- Actions : marquer comme lue, supprimer, voir le document associé
- Bouton pour marquer toutes les notifications comme lues

### 3. Types de notifications
- **INFO** : Informations générales (nouveau document assigné, etc.)
- **SUCCESS** : Actions réussies
- **WARNING** : Avertissements (document expirant bientôt, réassignation)
- **ERROR** : Erreurs (document expiré)

## Configuration

### 1. Vérification automatique de l'expiration
Pour activer la vérification automatique de l'expiration des documents, ajoutez cette commande au cron :

```bash
# Vérifier l'expiration des documents tous les jours à 8h00
0 8 * * * cd /chemin/vers/gestion_doc && python manage.py check_document_expiration
```

### 2. Exécution manuelle
Vous pouvez également exécuter la commande manuellement :

```bash
python manage.py check_document_expiration
```

## Utilisation

### 1. Accès aux notifications
- Cliquez sur l'icône de cloche dans la navbar pour voir les notifications récentes
- Cliquez sur "Voir toutes les notifications" pour accéder à la page complète
- Ou utilisez le lien "Notifications" dans la sidebar

### 2. Gestion des notifications
- **Marquer comme lue** : Cliquez sur une notification ou utilisez le bouton "Marquer comme lue"
- **Supprimer** : Utilisez le bouton "Supprimer" pour supprimer une notification
- **Marquer toutes comme lues** : Utilisez le bouton en haut de la page

### 3. Navigation
- Cliquez sur une notification pour accéder au document associé
- Les notifications avec URL vous redirigent automatiquement vers la page concernée

## Notifications automatiques

### 1. Expiration de documents
- **7 jours avant expiration** : Notification de type WARNING
- **Jour d'expiration** : Notification de type ERROR
- **Après expiration** : Notification de type ERROR

### 2. Création de documents
- **Agent assigné** : Notification quand un document lui est assigné
- **Gestionnaires/Administrateurs** : Notification de création de document

### 3. Modification de documents
- **Ancien propriétaire** : Notification de réassignation (WARNING)
- **Nouveau propriétaire** : Notification d'assignation (INFO)
- **Gestionnaires/Administrateurs** : Notification de modification

## Personnalisation

### 1. Modifier les délais d'expiration
Dans `views.py`, modifiez la fonction `check_document_expiration()` :

```python
# Documents expirant dans les X prochains jours
expiring_soon = Document.objects.filter(
    date_expiration__gte=today,
    date_expiration__lte=today + timedelta(days=7),  # Modifier cette valeur
    is_archived=False
)
```

### 2. Modifier les types de notifications
Dans les vues de documents, modifiez le paramètre `type` des notifications :

```python
create_notification(
    user=user,
    objet="Titre",
    message="Message",
    type='INFO',  # INFO, SUCCESS, WARNING, ERROR
    url='/url/'
)
```

### 3. Ajouter de nouveaux types de notifications
Dans `models.py`, modifiez les choix du modèle Notification :

```python
TYPE_CHOICES = [
    ('INFO', _('Information')),
    ('SUCCESS', _('Succès')),
    ('WARNING', _('Avertissement')),
    ('ERROR', _('Erreur')),
    ('CUSTOM', _('Personnalisé')),  # Nouveau type
]
```

## Dépannage

### 1. Notifications qui ne s'affichent pas
- Vérifiez que l'utilisateur a des permissions pour voir les notifications
- Vérifiez les erreurs JavaScript dans la console du navigateur
- Vérifiez que l'URL `notifications_ajax` fonctionne

### 2. Commandes de management qui ne fonctionnent pas
- Vérifiez que vous êtes dans le bon répertoire
- Vérifiez que les migrations ont été appliquées
- Vérifiez les logs Django pour les erreurs

### 3. Notifications dupliquées
- La commande `check_document_expiration` vérifie les doublons
- Les notifications similaires du même jour ne sont pas créées

## Sécurité

- Les notifications sont liées à l'utilisateur connecté
- Seul l'utilisateur peut voir et gérer ses propres notifications
- Les URLs des notifications sont validées
- Protection CSRF sur toutes les actions

## Performance

- Les notifications sont paginées pour éviter les problèmes de performance
- La vérification d'expiration utilise des requêtes optimisées
- Les notifications AJAX sont limitées à 5 éléments
- Actualisation automatique toutes les 30 secondes (configurable) 