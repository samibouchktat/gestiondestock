from django import forms
from django.forms import modelformset_factory

from .models import Article, Fournisseur, Commande, Avoir, CustomUser
from django import forms
from .models import Article, Fournisseur, Commande, Avoir, CustomUser, DemandeArticle
from django.conf import settings

from .models import UserProfile
from django.forms.models import BaseInlineFormSet
from .models import Commande, Avoir
from django import forms
from django.contrib.auth import get_user_model
from .models import Fournisseur
from .models import MouvementStock
from .models import DemandeArticle 
from django.forms import modelformset_factory
from django.contrib.auth.forms import UserCreationForm
from .models import Article, Fournisseur, Commande, Avoir, CustomUser, DemandeArticle
from django.conf import settings

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role')

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['nom', 'reference', 'description', 'prix', 'quantite', ]

    def clean(self):
        cleaned_data = super().clean()
        quantite = cleaned_data.get('quantite')
        if quantite is not None and quantite < 0:
            raise forms.ValidationError("La quantité ne peut pas être négative.")
        return cleaned_data

class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['etat', 'fournisseur', 'employe']

class AvoirForm(forms.ModelForm):
    class Meta:
        model = Avoir
        fields = ['article', 'quantite']

AvoirFormSet = modelformset_factory(Avoir, fields='__all__')

class ProfilForm(forms.Form):
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control highlight-yellow',
            'placeholder': 'Votre numéro de téléphone'
        })
    )
    class BaseAvoirFormSet(BaseInlineFormSet):
        def clean(self):
            super().clean()
            for form in self.forms:
                       if not form.cleaned_data or form.cleaned_data.get('DELETE'):
                             continue
            article = form.cleaned_data['article']
            qty     = form.cleaned_data['quantite']
            if qty > article.quantite:
                form.add_error('quantite',
                    f"Quantité maximale disponible : {article.quantite}")

class BaseAvoirFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE'):
                continue
            article = form.cleaned_data['article']
            qty     = form.cleaned_data['quantite']
            if qty > article.quantite:
                form.add_error('quantite',
                    f"Quantité maximale disponible : {article.quantite}")

class EmailVerificationForm(forms.Form):
    email = forms.EmailField(label="Votre adresse e-mail", max_length=254)

class OTPVerificationForm(forms.Form):
    code = forms.CharField(label="Code de vérification", max_length=6)

class FournisseurForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = Fournisseur
        fields = ['nom', 'contact', 'email', 'adresse']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class FournisseurUserForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=150, required=False)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput, required=False)
    email = forms.EmailField(label="Email")
    nom = forms.CharField(label="Nom du fournisseur", max_length=100)
    contact = forms.CharField(label="Contact", max_length=20)
    adresse = forms.CharField(label="Adresse", max_length=255, required=False)

class MouvementStockForm(forms.ModelForm):
    class Meta:
        model = MouvementStock
        fields = ['article', 'quantite', 'motif']

from django import forms

class DemandeArticleForm(forms.ModelForm):
    class Meta:
        model = DemandeArticle
        fields = ['article', 'quantite', 'gestionnaire']
        widgets = {
            'article': forms.Select(attrs={'class': 'form-select'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'gestionnaire': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gestionnaire'].queryset = CustomUser.objects.filter(role='gestionnaire')

class MouvementForm(forms.ModelForm):
    class Meta:
        model = MouvementStock
        fields = ['article', 'quantite', 'motif'] 

class ArticleUpdateForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['quantite']

class EntreeStockForm(forms.ModelForm):
    class Meta:
        model = MouvementStock  
        fields = ['article', 'quantite', 'motif', 'type_mouvement']
