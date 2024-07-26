# tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import Contrat

@shared_task
def check_contracts():
    today = timezone.now().date()
    notify_date = today + timedelta(days=5)
    
    # Contrats arrivant à expiration dans 5 jours
    contracts_to_notify = Contrat.objects.filter(date_fin=notify_date, statut='En cours')
    for contrat in contracts_to_notify:
        # Envoyer un email de notification
        send_mail(
            'Contrat arrivant à expiration',
            f'Salutation, le contrat de {contrat.salarie} avec {contrat.entreprise} se termine le {contrat.date_fin}.',
            'from@example.com',
            [contrat.salarie.email, contrat.entreprise.email],
        )
    
    # Contrats arrivant à expiration aujourd'hui
    contracts_to_terminate = Contrat.objects.filter(date_fin=today, statut='En cours')
    for contrat in contracts_to_terminate:
        # Mettre à jour le statut
        contrat.statut = 'Terminé'
        contrat.save()
        # Envoyer un email de notification
        send_mail(
            'Contrat terminé',
            f'Bonjour, le contrat de {contrat.salarie} avec {contrat.entreprise} se termine aujourd\'hui.',
            'from@example.com',
            [contrat.salarie.email, contrat.entreprise.email],
        )
