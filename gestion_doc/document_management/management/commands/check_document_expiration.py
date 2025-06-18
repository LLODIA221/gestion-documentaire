from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from document_management.models import Document, Notification


class Command(BaseCommand):
    help = 'Vérifie l\'expiration des documents et crée des notifications'

    def handle(self, *args, **options):
        today = timezone.now().date()
        
        # Documents expirant dans les 7 prochains jours
        expiring_soon = Document.objects.filter(
            date_expiration__gte=today,
            date_expiration__lte=today + timedelta(days=7),
            is_archived=False
        )
        
        # Documents expirés
        expired = Document.objects.filter(
            date_expiration__lt=today,
            is_archived=False
        )
        
        notifications_created = 0
        
        # Créer des notifications pour les documents expirant bientôt
        for document in expiring_soon:
            days_until_expiry = (document.date_expiration - today).days
            
            # Vérifier si une notification similaire existe déjà aujourd'hui
            existing_notification = Notification.objects.filter(
                user=document.agent.user,
                objet="Expiration de document",
                message__contains=document.libelle,
                date_creation__date=today
            ).first()
            
            if not existing_notification:
                if days_until_expiry == 0:
                    message = f"Le document '{document.libelle}' expire aujourd'hui !"
                    notification_type = 'ERROR'
                else:
                    message = f"Le document '{document.libelle}' expire dans {days_until_expiry} jour(s)."
                    notification_type = 'WARNING'
                
                Notification.objects.create(
                    user=document.agent.user,
                    objet="Expiration de document",
                    message=message,
                    type=notification_type,
                    url=f'/documents/detail/{document.id}/'
                )
                notifications_created += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Notification créée pour {document.agent.user.username}: {message}')
                )
        
        # Créer des notifications pour les documents expirés
        for document in expired:
            # Vérifier si une notification similaire existe déjà aujourd'hui
            existing_notification = Notification.objects.filter(
                user=document.agent.user,
                objet="Document expiré",
                message__contains=document.libelle,
                date_creation__date=today
            ).first()
            
            if not existing_notification:
                Notification.objects.create(
                    user=document.agent.user,
                    objet="Document expiré",
                    message=f"Le document '{document.libelle}' a expiré le {document.date_expiration}.",
                    type='ERROR',
                    url=f'/documents/detail/{document.id}/'
                )
                notifications_created += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Notification créée pour {document.agent.user.username}: Document expiré {document.libelle}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Terminé. {notifications_created} notification(s) créée(s).')
        ) 