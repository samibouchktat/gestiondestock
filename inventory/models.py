from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
import random, string
from datetime import timedelta
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth import get_user_model


# Utilisateur personnalisé avec rôles
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('gestionnaire', 'Gestionnaire de stock'),
        ('employe', 'Employé'),
        ('fournisseur', 'Fournisseur'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    # Garder une seule définition de secondary_email :
    secondary_email = models.EmailField(
        "Email secondaire (2FA)",
        max_length=254,
        blank=True,
        null=True,
        unique=True,
        help_text="Adresse e-mail ajoutée via la procédure 2FA"
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
# Fournisseur
class Fournisseur(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE,
        limit_choices_to={'role': 'fournisseur'},
        related_name='fournisseur_profile',
        null=True, blank=True  # ← autorise les fournisseurs sans user
    )
    nom     = models.CharField(max_length=100)
    contact = models.CharField(max_length=20)
    email   = models.EmailField(unique=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nom


# Article
class Article(models.Model):
    nom           = models.CharField(max_length=200)
    reference     = models.CharField(max_length=100, unique=True)
    prix          = models.DecimalField(max_digits=10, decimal_places=2)
    quantite      = models.IntegerField(default=0, help_text="Quantité initiale")
    stock         = models.IntegerField(default=0, help_text="Stock courant")
    description   = models.TextField(blank=True, default="")
    facteur_co2   = models.FloatField(default=0.0, verbose_name="Facteur CO₂ (kg/unité)")
    stock_min     = models.PositiveIntegerField(default=1, help_text="Seuil minimal pour alerte")
    alerte_stock_faible_envoyee = models.BooleanField(
        default=False,
        help_text="Passé à True dès qu'une alerte stock < 10 a été envoyée"
    )

    def __str__(self):
        return f"{self.nom} ({self.reference})"

def save(self, *args, **kwargs):
    if self.pk:  # L'article existe déjà → on met à jour le stock si la quantité a changé
        old = Article.objects.get(pk=self.pk)
        delta = self.quantite - old.quantite
        self.stock += delta
    else:
        self.stock = self.quantite
    super().save(*args, **kwargs)

        # Alerte de stock critique
    if self.stock < self.stock_min and not self.alerte_stock_faible_envoyee:
            self.envoyer_alerte_stock_critique()
            Article.objects.filter(pk=self.pk).update(alerte_stock_faible_envoyee=True)
        
    elif self.stock >= self.stock_min and self.alerte_stock_faible_envoyee:
            Article.objects.filter(pk=self.pk).update(alerte_stock_faible_envoyee=False)

def envoyer_alerte_stock_critique(self):
        User = get_user_model()
        destinataires = User.objects.filter(
            role="gestionnaire",
            is_active=True,
            secondary_email__isnull=False
        ).values_list("secondary_email", flat=True)

        if not destinataires:
            return

        sujet = f"⚠️ Alerte stock critique : {self.nom}"
        corps = (
            f"Bonjour,\n\n"
            f"L’article « {self.nom} » (Réf : {self.reference}) est à un niveau critique.\n"
            f"Quantité actuelle : {self.stock} unités (Seuil minimal : {self.stock_min}).\n\n"
            f"Merci de réapprovisionner dès que possible.\n\n"
            f"Cordialement,\n"
            f"GestionStock PRO"
        )

        send_mail(
            sujet,
            corps,
            settings.DEFAULT_FROM_EMAIL,
            list(destinataires),
            fail_silently=False,
        )

def envoyer_alerte_stock_critique(self, declencheur=None):
    User = get_user_model()

    if not declencheur:
        return  # Aucun utilisateur identifié pour déclencher

    role = declencheur.role
    article_nom = self.nom
    article_ref = self.reference

    # Sujet et message personnalisés selon le rôle
    if role == "gestionnaire":
        sujet = f"⚠️ Alerte Stock Critique : {article_nom}"
        corps = (
            f"Bonjour,\n\n"
            f"L’article « {article_nom} » (Réf : {article_ref}) est sous le seuil critique.\n"
            f"Veuillez contacter un fournisseur pour réapprovisionnement.\n\n"
            f"Cordialement,\nGestionStock PRO"
        )
    elif role == "employe":
        sujet = f"⚠️ Alerte Stock Faible détectée"
        corps = (
            f"Bonjour,\n\n"
            f"L’article « {article_nom} » (Réf : {article_ref}) a un stock critique.\n"
            f"Veuillez en informer votre gestionnaire de stock pour action immédiate.\n\n"
            f"Cordialement,\nGestionStock PRO"
        )
    else:
        # Autres rôles → on n'envoie rien
        return

    # Envoi uniquement si secondary_email est défini
    email = declencheur.secondary_email
    if email:
        send_mail(
            sujet,
            corps,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False
        )
# Mouvements de stock
class Stock(models.Model):
    article      = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='anciennes_entrees'  
    )
    entree       = models.IntegerField(default=0)
    sortie       = models.IntegerField(default=0)
    date_entree  = models.DateField(null=True, blank=True)
    date_sortie  = models.DateField(null=True, blank=True)
    etat         = models.CharField(max_length=100)
    description  = models.TextField(blank=True, default="")

    def __str__(self):
        return f"MvtStock {self.id} : {self.article.nom} +{self.entree}/-{self.sortie}"

# Commande et détails
class Commande(models.Model):
    date       = models.DateField(auto_now_add=True)
    etat       = models.CharField(max_length=100)
    fournisseur= models.ForeignKey(Fournisseur, on_delete=models.CASCADE)
    employe    = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'employe'})

    def __str__(self):
        return f"Commande {self.id} - {self.etat}"

    def total_price(self):
        return sum(
            avoir.quantite * avoir.article.prix
            for avoir in self.articles_commande.all()
        )

class Avoir(models.Model):
    
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='articles_commande')
    article  = models.ForeignKey(Article, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantite} x {self.article.nom} (Cmd {self.commande.id})"

# Rapport IA
class Rapport(models.Model):
    titre         = models.CharField(max_length=100)
    date_creation = models.DateTimeField(auto_now_add=True)
    contenu       = models.TextField()
    auteur        = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'admin'})

    def __str__(self):
        return f"{self.titre} ({self.date_creation.date()})"

# Messagerie interne
class Message(models.Model):
    sender    = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver  = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    content   = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read   = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"

# 2FA
class TwoFactorCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    expiration_time = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        from django.utils import timezone
        return not self.is_used and self.expiration_time > timezone.now()

    def is_expired(self):
        return timezone.now() > self.expiration_time

    @staticmethod
    def generate_code():
        return ''.join(random.choices(string.digits, k=6))

    @classmethod
    def create_code(cls, user):
        code = cls.generate_code()
        expiration_time = timezone.now() + timedelta(minutes=10)
        return cls.objects.create(user=user, code=code, expiration_time=expiration_time)
class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    phone   = models.CharField("Téléphone", max_length=20, blank=True)
    address = models.TextField("Adresse", blank=True)

    def __str__(self):
        return f"{self.user.username} — Profil"



@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

class MouvementStock(models.Model):
    TYPE_CHOICES = [
        ('entree', 'Entrée'),
        ('sortie', 'Sortie'),
    ]
    article         = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='movements'
    )
    type_mouvement  = models.CharField(max_length=10, choices=TYPE_CHOICES)
    quantite        = models.PositiveIntegerField()
    date            = models.DateTimeField(auto_now_add=True)
    user            = models.ForeignKey(
                        settings.AUTH_USER_MODEL,
                        on_delete=models.SET_NULL,
                        null=True, blank=True
                     )
    motif           = models.CharField(max_length=255, blank=True)

    @property
    def entree(self):
        return self.quantite if self.type_mouvement == 'entree' else 0

    @property
    def sortie(self):
        return self.quantite if self.type_mouvement == 'sortie' else 0

def save(self, *args, **kwargs):
    # Annule l'effet de l'ancien mouvement si modification
    if self.pk:
        ancien = MouvementStock.objects.get(pk=self.pk)
        if ancien.type_mouvement == 'entree':
            self.article.stock -= ancien.quantite
        else:
            self.article.stock += ancien.quantite

    # Applique le nouveau mouvement
    if self.type_mouvement == 'entree':
        self.article.stock += self.quantite
    else:  # sortie
        if self.quantite > self.article.stock:
            raise ValueError("Stock insuffisant pour effectuer la sortie.")
        self.article.stock -= self.quantite

    # Sauvegarde l'article
    self.article.save()
    super().save(*args, **kwargs)

    # Alerte si stock < 10
    if self.article.stock < 10 and self.user:
        destinataire = self.user.secondary_email
        if not destinataire:
            return  # Pas d'email secondaire défini

        role = self.user.role
        sujet = f"⚠️ Alerte : Stock faible pour « {self.article.nom} »"

        if role == 'gestionnaire':
            corps = (
                f"Bonjour {self.user.username},\n\n"
                f"Le stock de l’article « {self.article.nom} » (Réf : {self.article.reference}) "
                f"est critique (stock = {self.article.stock}).\n"
                f"Veuillez contacter un fournisseur pour réapprovisionnement.\n\n"
                f"Cordialement,\nGestionStock PRO"
            )
        elif role == 'employe':
            corps = (
                f"Bonjour {self.user.username},\n\n"
                f"Le stock de l’article « {self.article.nom} » (Réf : {self.article.reference}) "
                f"est très bas (stock = {self.article.stock}).\n"
                f"Veuillez alerter votre gestionnaire pour commande urgente.\n\n"
                f"Cordialement,\nGestionStock PRO"
            )
        else:
            return  # autre rôle : pas d'envoi

        send_mail(
            sujet,
            corps,
            settings.DEFAULT_FROM_EMAIL,
            [destinataire],
            fail_silently=False,
        )

class DemandeArticle(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuvee', 'Approuvée'),
        ('refusee', 'Refusée'),
    ]

    employe = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'employe'})
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    # Si tu as un modèle Categorie, garde-le, sinon retire ce champ :
    date_demande = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')

    def __str__(self):
        return f"{self.article.nom} ({self.quantite}) par {self.employe.username}"

