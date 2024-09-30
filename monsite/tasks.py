
from celery import shared_task
from .views import send_newsletter

@shared_task
def scheduled_newsletter():
    subject = "Newsletter mensuelle"
    message = "Ceci est notre dernière mise à jour..."
    send_newsletter(subject, message)
