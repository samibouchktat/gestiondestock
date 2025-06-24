import random
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from .models import EmailOTP
from django.conf import settings


def send_email_otp(user):
    code    = f"{random.randint(0, 999999):06d}"
    expires = timezone.now() + timedelta(minutes=10)
    EmailOTP.objects.create(user=user, code=code, valid_until=expires)
    subject = "Votre code de vérification"
    message = (f"Bonjour {user.username},\n\n"
               f"Votre code de connexion est : {code}\n"
               "Valide 10 minutes.")
    send_mail(
    subject,
    message,
  #  settings.gestiondestock0@gmail.com,   # <-- ici on passe bien l’adresse Gmail
    [user.email],
)


