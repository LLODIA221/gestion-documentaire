from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator,MaxLengthValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
import uuid

# Modèle de base abstrait pour les champs communs
class BaseTimeStampModel(models.Model):
    """
    Classe de base abstraite pour fournir des champs d'horodatage communs
    """
    date_creation = models.DateTimeField(_("Date de création"), auto_now_add=True)
    date_modification = models.DateTimeField(_("Date de modification"), auto_now=True)
    
    class Meta:
        abstract = True


class Delegation(BaseTimeStampModel):
    """
    Modèle représentant une délégation
    """
    nom_delegation = models.CharField(
        _( "Nom de la délégation"), max_length=100, unique=True, 
        validators=[MaxLengthValidator(100)]
    )
    localisation = models.CharField(
        _( "Localisation"), max_length=255, 
        validators=[MaxLengthValidator(255)]
    )
    description = models.TextField(
        _( "Description"), validators=[MaxLengthValidator(500)]
    )
    
    class Meta:
        verbose_name = _( "Délégation")
        verbose_name_plural = _( "Délégations")
        ordering = ['nom_delegation']
    
    def __str__(self):
        return self.nom_delegation

class Structure(BaseTimeStampModel):
    """
    Modèle représentant une structure organisationnelle
    """
    nom = models.CharField(
        _( "Nom"), max_length=100, unique=True, 
        validators=[MaxLengthValidator(100)]
    )
    description = models.TextField(
        _( "Description"), validators=[MaxLengthValidator(500)]
    )
    structure_parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, 
        related_name='enfants', verbose_name=_("Structure parente")
    )
    delegation = models.ForeignKey(
        Delegation, on_delete=models.CASCADE, verbose_name=_("Délégation"), 
        related_name="structures",null=True, blank=True
    )
    
    def clean(self):
        """Validation pour empêcher une structure d'être son propre parent."""
        if self.structure_parent and self.structure_parent.id == self.id:
            raise ValidationError("Une structure ne peut pas être son propre parent.")
    
    class Meta:
        verbose_name = _( "Structure")
        verbose_name_plural = _( "Structures")
        ordering = ['nom']
    
    def __str__(self):
        return self.nom

class Permission(models.Model):
    """
    Modèle représentant une permission système
    """
    ENTITY_CHOICES = [
        ('DELEGATION', _('Délégation')),
        ('STRUCTURE', _('Structure')),
        ('CATEGORIE_DOCUMENTS', _('Catégorie Documents')),
        ('DOCUMENTS', _('Documents')),
        ('ROLES', _('Rôles')),
        ('AGENTS', _('Agents')),
        ('USERS', _('Utilisateurs')),
        ('NOTIFICATIONS', _('Notifications')),
        ('DEMANDES', _('Demandes')),
    ]
    
    ACTION_CHOICES = [
        ('CREATE', _('Créer')),
        ('READ', _('Lire')),
        ('UPDATE', _('Modifier')),
        ('DELETE', _('Supprimer')),
    ]
    
    entity = models.CharField(_("Entité"), max_length=50, choices=ENTITY_CHOICES)
    action = models.CharField(_("Action"), max_length=10, choices=ACTION_CHOICES)
    description = models.CharField(_("Description"), max_length=255, blank=True)

    class Meta:
        verbose_name = _("Permission")
        verbose_name_plural = _("Permissions")
        unique_together = ['entity', 'action']
        ordering = ['entity', 'action']

    def __str__(self):
        return f"{self.action}_{self.entity}"

    def save(self, *args, **kwargs):
        if not self.description:
            self.description = f"Permission de {self.get_action_display().lower()} {self.get_entity_display().lower()}"
        super().save(*args, **kwargs)





class Role(models.Model):
    """
    Modèle représentant les rôles utilisateur
    """
    ROLE_CHOICES = [
        ('ADMIN', _('Administrateur')),
        ('AGENT', _('Agent')),
        ('GESTIONNAIRE', _('Gestionnaire')),
        ('CONTROLLER', _('Contrôleur')),
    ]

    ROLE_NIVEAUX = {
        'ADMIN': 4,
        'GESTIONNAIRE': 3,
        'CONTROLLER': 2,
        'AGENT': 1,
    }

    libelle = models.CharField("Libellé", max_length=20, choices=ROLE_CHOICES, unique=True)
    niveau = models.PositiveIntegerField(
        "Niveau",
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    description = models.TextField("Description")
    permissions = models.ManyToManyField(
        Permission,
        related_name="roles",
        verbose_name="Permissions"
    )

    class Meta:
        verbose_name = "Rôle"
        verbose_name_plural = "Rôles"
        ordering = ['niveau']

    def __str__(self):
        return self.libelle

    def save(self, *args, **kwargs):
        # Fixer automatiquement le niveau selon le libellé
        if self.libelle in self.ROLE_NIVEAUX:
            self.niveau = self.ROLE_NIVEAUX[self.libelle]
        else:
            self.niveau = 1  # Valeur par défaut
        super().save(*args, **kwargs)

    def get_permissions_list(self):
        return ", ".join([str(permission) for permission in self.permissions.all()])



class Agent(BaseTimeStampModel):
    """
    Modèle représentant un agent
    """
    MATRICULE_REGEX = r'^\d{6}/[A-Z]$'
    NOM_PRENOM_REGEX = r'^[a-zA-ZÀ-ÿ\s\-\']+$'
    PHONE_REGEX = r'^(\+\d{1,3})?\d{9,15}$'
    
    matricule = models.CharField(
        _("Matricule"),
        max_length=8,
        unique=True,
        validators=[
            RegexValidator(
                regex=MATRICULE_REGEX,
                message=_("Le matricule doit être au format 123456/X")
            )
        ]
    )
    prenom = models.CharField(
        _("Prénom"),
        max_length=50,
        validators=[
            RegexValidator(
                regex=NOM_PRENOM_REGEX,
                message=_("Le prénom ne doit contenir que des lettres, espaces et tirets")
            )
        ]
    )
    nom = models.CharField(
        _("Nom"),
        max_length=50,
        validators=[
            RegexValidator(
                regex=NOM_PRENOM_REGEX,
                message=_("Le nom ne doit contenir que des lettres, espaces et tirets")
            )
        ]
    )
    date_naissance = models.DateField(_("Date de naissance"))
    lieu_naissance = models.CharField(_("Lieu de naissance"), max_length=255)
    adresse = models.CharField(_("Adresse"), max_length=255)
    email = models.EmailField(_("Email"), unique=True)
    telephone = models.CharField(
        _("Téléphone"),
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=PHONE_REGEX,
                message=_("Numéro de téléphone invalide. Format: +221xxxxxxxxx")
            )
        ]
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="agent_profile",
        verbose_name=_("Utilisateur")
    )
    structure = models.ForeignKey(
        Structure, 
        on_delete=models.PROTECT,
        related_name="agents",
        verbose_name=_("Structure")
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="agents",
        verbose_name=_("Rôle")
    )
    is_active = models.BooleanField(_("Actif"), default=True)
    
    class Meta:
        verbose_name = _("Agent")
        verbose_name_plural = _("Agents")
        ordering = ['nom', 'prenom']
    
    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.matricule})"
    
    def clean(self):
        # Validation supplémentaire
        today = timezone.now().date()
        if self.date_naissance and self.date_naissance > today:
            raise ValidationError({'date_naissance': _("La date de naissance ne peut pas être dans le futur")})
    
    def get_full_name(self):
        return f"{self.prenom} {self.nom}"


class CategorieDocument(BaseTimeStampModel):
    """
    Modèle représentant les catégories de documents
    """
    TYPE_ACCES_CHOICES = [
        ('PRIVATE', _('Privé')),
        ('PUBLIC', _('Public')),
        ('RESTRICTED', _('Restreint')),
    ]
    
    libelle = models.CharField(_("Libellé"), max_length=50, unique=True)
    description = models.TextField(_("Description"))
    type_acces = models.CharField(
        _("Type d'accès"),
        max_length=10,
        choices=TYPE_ACCES_CHOICES,
        default='PRIVATE'
    )
    
    class Meta:
        verbose_name = _("Catégorie de document")
        verbose_name_plural = _("Catégories de documents")
        ordering = ['libelle']
    
    def __str__(self):
        return self.libelle
    


class Document(BaseTimeStampModel):
    """
    Modèle représentant un document
    """
    TYPE_CHOICES = [
        ('PDF', 'PDF'),
        ('JPEG', 'JPEG'),
        ('PNG', 'PNG'),
        ('DOCX', 'DOCX'),
        ('XLSX', 'XLSX')
    ]
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    libelle = models.CharField(_("Libellé"), max_length=100)
    reference = models.CharField(_("Référence"), max_length=50, unique=True, blank=True)
    fichier = models.FileField(_("Fichier"), upload_to='documents/%Y/%m/')
    type = models.CharField(_("Type"), max_length=10, choices=TYPE_CHOICES)
    date_expiration = models.DateField(_("Date d'expiration"), null=True, blank=True)
    categorie_document = models.ForeignKey(
        CategorieDocument, 
        on_delete=models.PROTECT,
        related_name="documents",
        verbose_name=_("Catégorie")
    )
    agent = models.ForeignKey(
        Agent, 
        on_delete=models.PROTECT,
        related_name="documents",
        verbose_name=_("Agent")
    )
    is_archived = models.BooleanField(_("Archivé"), default=False)
    
    class Meta:
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")
        ordering = ['-date_creation']
        unique_together = ['libelle', 'agent']
    
    def __str__(self):
        return f"{self.libelle} ({self.get_type_display()})"
    
    def clean(self):
        # Validation: date d'expiration doit être postérieure à la date d'ajout
        if self.date_expiration and self.date_expiration <= timezone.now().date():
            raise ValidationError({
                'date_expiration': _("La date d'expiration doit être postérieure à aujourd'hui")
            })
    
    def save(self, *args, **kwargs):
        # Génération d'une référence unique si non définie
        if not self.reference:
            today = timezone.now().date()
            prefix = f"DOC-{today.year}{today.month:02d}"
            last_doc = Document.objects.filter(reference__startswith=prefix).order_by('reference').last()
            
            if last_doc:
                # Extraction du numéro depuis la dernière référence
                try:
                    seq = int(last_doc.reference.split('-')[-1]) + 1
                except (ValueError, IndexError):
                    seq = 1
            else:
                seq = 1
                
            self.reference = f"{prefix}-{seq:04d}"
            
        super().save(*args, **kwargs)

    def get_latest_version(self):
        return self.versions.order_by('-version_number').first()


class DocumentVersion(BaseTimeStampModel):
    """
    Modèle représentant les versions d'un document
    """
    document = models.ForeignKey(
        Document, 
        related_name='versions', 
        on_delete=models.CASCADE,
        verbose_name=_("Document")
    )
    fichier = models.FileField(_("Fichier"), upload_to='document_versions/%Y/%m/')
    type = models.CharField(_("Type"), max_length=10, choices=Document.TYPE_CHOICES)
    version_number = models.PositiveIntegerField(_("Numéro de version"), default=1)
    change_summary = models.TextField(_("Résumé des modifications"), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="document_versions",
        verbose_name=_("Créé par")
    )
    
    class Meta:
        verbose_name = _("Version de document")
        verbose_name_plural = _("Versions de documents")
        ordering = ['-date_creation']
        unique_together = ['document', 'version_number']
    
    def __str__(self):
        return f"{self.document.libelle} v{self.version_number}"

    def save(self, *args, **kwargs):
        if not self.version_number:
            last_version = DocumentVersion.objects.filter(document=self.document).order_by('-version_number').first()
            if last_version:
                self.version_number = last_version.version_number + 1
            else:
                self.version_number = 1
        super().save(*args, **kwargs)


class Demande(BaseTimeStampModel):
    """
    Modèle représentant une demande
    """
    STATUT_CHOICES = [
        ('EN_ATTENTE', _('En attente')),
        ('EN_COURS', _('En cours de traitement')),
        ('VALIDEE', _('Validée')),
        ('REJETEE', _('Rejetée')),
        ('ANNULEE', _('Annulée')),
    ]
    
    reference = models.CharField(_("Référence"), max_length=20, unique=True, blank=True)
    objet_demande = models.CharField(_("Objet"), max_length=100)
    message = models.TextField(_("Message"))
    statut = models.CharField(
        _("Statut"),
        max_length=20, 
        choices=STATUT_CHOICES,
        default='EN_ATTENTE'
    )
    date_traitement = models.DateTimeField(_("Date de traitement"), null=True, blank=True)
    demandeur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="demandes",
        verbose_name=_("Demandeur")
    )
    gestionnaire = models.ForeignKey(
        Agent,
        on_delete=models.PROTECT,
        related_name="demandes_gerees",
        verbose_name=_("Gestionnaire"),
        null=True,
        blank=True
    )
    documents = models.ManyToManyField(
        Document, 
        related_name="demandes",
        blank=True,
        verbose_name=_("Documents")
    )
    
    class Meta:
        verbose_name = _("Demande")
        verbose_name_plural = _("Demandes")
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.reference} - {self.objet_demande}"
    
    def save(self, *args, **kwargs):
        # Génération d'une référence unique si non définie
        if not self.reference:
            today = timezone.now().date()
            prefix = f"DEM-{today.year}{today.month:02d}"
            last_demande = Demande.objects.filter(reference__startswith=prefix).order_by('reference').last()
            
            if last_demande:
                # Extraction du numéro depuis la dernière référence
                try:
                    seq = int(last_demande.reference.split('-')[-1]) + 1
                except (ValueError, IndexError):
                    seq = 1
            else:
                seq = 1
                
            self.reference = f"{prefix}-{seq:04d}"
            
        # Définition de la date_traitement quand le statut change pour VALIDEE ou REJETEE
        if self.statut in ['VALIDEE', 'REJETEE'] and not self.date_traitement:
            self.date_traitement = timezone.now()
            
        super().save(*args, **kwargs)


class DemandeMessage(BaseTimeStampModel):
    """
    Modèle représentant les messages liés à une demande
    """
    demande = models.ForeignKey(
        Demande, 
        related_name='messages', 
        on_delete=models.CASCADE,
        verbose_name=_("Demande")
    )
    emetteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT,
        related_name="messages_envoyes",
        verbose_name=_("Émetteur")
    )
    message = models.TextField(_("Message"))
    motif_rejet = models.TextField(_("Motif de rejet"), null=True, blank=True)
    document_joint = models.FileField(_("Document joint"), upload_to='demande_documents/', null=True, blank=True)
    is_internal = models.BooleanField(_("Message interne"), default=False, help_text=_("Message visible uniquement par les gestionnaires"))
    
    class Meta:
        verbose_name = _("Message de demande")
        verbose_name_plural = _("Messages de demande")
        ordering = ['date_creation']
    
    def __str__(self):
        return f"Message de {self.emetteur} pour {self.demande}"


class Journal(models.Model):
    """
    Modèle pour journaliser les activités du système
    """
    ACTION_CHOICES = [
        ('CREATE', _('Création')),
        ('READ', _('Lecture')),
        ('UPDATE', _('Modification')),
        ('DELETE', _('Suppression')),
        ('LOGIN', _('Connexion')),
        ('LOGOUT', _('Déconnexion')),
        ('OTHER', _('Autre')),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT,
        related_name="journal_entries",
        verbose_name=_("Utilisateur")
    )
    action = models.CharField(_("Action"), max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(_("Modèle"), max_length=50, blank=True)
    object_id = models.CharField(_("ID Objet"), max_length=50, blank=True)
    details = models.TextField(_("Détails"), blank=True)
    ip_address = models.GenericIPAddressField(_("Adresse IP"), blank=True, null=True)
    timestamp = models.DateTimeField(_("Horodatage"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("Journal")
        verbose_name_plural = _("Journaux")
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.timestamp}"


class Notification(models.Model):
    """
    Modèle pour les notifications utilisateur
    """
    TYPE_CHOICES = [
        ('INFO', _('Information')),
        ('SUCCESS', _('Succès')),
        ('WARNING', _('Avertissement')),
        ('ERROR', _('Erreur')),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("Utilisateur")
    )
    objet = models.CharField(_("Objet"), max_length=255)
    message = models.TextField(_("Message"))
    type = models.CharField(_("Type"), max_length=10, choices=TYPE_CHOICES, default='INFO')
    url = models.CharField(_("URL"), max_length=255, blank=True, help_text=_("URL associée à la notification"))
    date_creation = models.DateTimeField(_("Date de création"), auto_now_add=True)
    is_read = models.BooleanField(_("Lue"), default=False)
    date_lecture = models.DateTimeField(_("Date de lecture"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.objet} - {self.user}"
    
    def mark_as_read(self):
        """Marquer la notification comme lue"""
        if not self.is_read:
            self.is_read = True
            self.date_lecture = timezone.now()
            self.save(update_fields=['is_read', 'date_lecture'])