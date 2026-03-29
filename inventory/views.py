import os
from django.db.models import F
from django.shortcuts import render
from django.utils.timezone import now
from django.db.models import F
from httpx import request
from .models import Article
import json
from django.http import HttpResponse
import datetime
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.utils import timezone
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import never_cache
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.forms import inlineformset_factory
from .forms import AvoirForm
from .models import Commande, Avoir
from .models import Fournisseur
from .forms import FournisseurForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from .models import Article, Fournisseur, Stock, Commande
from django.utils import timezone
from datetime import timedelta
from .forms import FournisseurUserForm
from django.contrib.auth import get_user_model
from .models import Article, MouvementStock
from .forms import MouvementStockForm
from django.http import HttpResponse
import pandas as pd
from .forms import MouvementForm
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import DemandeArticleForm
import pytz
from .models import Article
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from .utils import generate_report
from django.http import JsonResponse
from .forms import ArticleUpdateForm
AvoirFormSet = inlineformset_factory(Commande, Avoir, fields=('article','quantite'), extra=1, can_delete=True)
from .models import (
    Article, Stock, Fournisseur, Commande, Avoir,
    Message, CustomUser, UserProfile, TwoFactorCode,DemandeArticle,
)
from .forms import (
    ArticleForm, 
    CommandeForm, BaseAvoirFormSet,
    EmailVerificationForm, OTPVerificationForm,DemandeArticleForm,

)
from .utils import generate_report
from django.db.models import F


from django.utils import timezone
import datetime

now = timezone.now()  

def is_manager(user):
    return getattr(user, "role", None) in {"gestionnaire", "admin"}


def home(request):
    return render(request, 'first.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "Nom d’utilisateur ou mot de passe incorrect.")
            return redirect("login")

        login(request, user)

        if user.is_superuser or user.role == "admin":
            return redirect('/admin/')
        elif user.role == "gestionnaire":
            return redirect('dashboard_gestionnaire')
        elif user.role == "employe":
            return redirect('dashboard_employe')
        else:
            messages.error(request, "Rôle utilisateur inconnu.")
            logout(request)
            return redirect("login")

    return render(request, "login.html")


@login_required
def redirect_dashboard(request):
    user = request.user
    if user.is_superuser or user.role == "admin":
        return redirect('/admin/')
    if user.role == "gestionnaire":
        return redirect('dashboard_gestionnaire')
    if user.role == "employe":
        return redirect('dashboard_employe')
    messages.error(request, "Rôle utilisateur inconnu.")
    return redirect('login')

@never_cache
def log_out(request):
    logout(request)
    messages.success(request, "Vous êtes maintenant déconnecté.")
    return redirect('login')
@login_required
def dashboard_gestionnaire(request):
    stock_total = Article.objects.aggregate(total=Sum('stock'))['total'] or 0
    cmd_count = Commande.objects.filter(etat__in=['en_attente', 'en cours']).count()
    critical_count = Article.objects.filter(stock__lt=F('stock_min')).count()
    fourn_count = Fournisseur.objects.count()

    low_stock_items = Article.objects.filter(stock__lt=F('stock_min')).order_by('stock')

    context = {
        "stock_total": stock_total,
        "cmd_count": cmd_count,
        "critical_count": critical_count,
        "fourn_count": fourn_count,
        "low_stock_items": low_stock_items,
    }
    return render(request, "dashboard_gestionnaire.html", context)



@login_required
def api_activites_recent(request):
    casablanca_tz = pytz.timezone('Africa/Casablanca')
    mouvements = MouvementStock.objects.select_related('article', 'user').order_by('-date')[:5]
    commandes = Commande.objects.select_related('fournisseur', 'employe').order_by('-date')[:5]

    activites = []

    def to_casablanca_time(dt):
        if isinstance(dt, datetime.date) and not isinstance(dt, datetime.datetime):
            dt = datetime.datetime.combine(dt, datetime.time())
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
        return dt.astimezone(casablanca_tz)

    for m in mouvements:
        date_locale = to_casablanca_time(m.date)
        activites.append({
            'type': 'mouvement',
            'sous_type': m.type_mouvement,
            'date': date_locale.strftime('%d/%m/%Y %H:%M'),
            'titre': f"{'Entrée' if m.type_mouvement == 'entree' else 'Sortie'} de stock",
            'description': f"{m.quantite} x {m.article.nom} {'ajoutés' if m.type_mouvement == 'entree' else 'sortis'} par {m.user.username if m.user else 'N/A'}",
        })

    for c in commandes:
        date_locale = to_casablanca_time(c.date)
        activites.append({
            'type': 'commande',
            'date': date_locale.strftime('%d/%m/%Y %H:%M'),
            'titre': f"Commande #{c.id}",
            'description': f"À {c.fournisseur.nom if c.fournisseur else ''} par {c.employe.username if hasattr(c, 'employe') and c.employe else 'N/A'}",
        })

    activites = sorted(activites, key=lambda x: x['date'], reverse=True)[:7]

    return JsonResponse({'activites': activites})
@login_required
def dashboard_employe(request):
    return render(request, 'dashboard_employe.html')



@login_required
def dashboard_admin(request):
    return render(request, 'dashboard_admin.html')

from django.contrib import messages

@login_required
def dashboard_fournisseur(request):
    try:
        fournisseur = Fournisseur.objects.get(user=request.user)
    except Fournisseur.DoesNotExist:
        messages.error(request, "Aucun fournisseur associé à ce compte utilisateur.")
        return redirect('login')  

    commandes = Commande.objects.filter(fournisseur=fournisseur)
    
    search = request.GET.get("search", "")
    filtre_etat = request.GET.get("filtre_etat", "")
    if search:
        commandes = commandes.filter(id__icontains=search)
    if filtre_etat:
        commandes = commandes.filter(etat=filtre_etat)
    
    nb_en_attente = commandes.filter(etat="en_attente").count()
    nb_validees = commandes.filter(etat="validée").count()
    nb_refusees = commandes.filter(etat="refusée").count()
    nb_total = commandes.count()
    montant_total = commandes.annotate(
        total=Sum(F('articles_commande__quantite') * F('articles_commande__article__prix'))
    ).aggregate(m=Sum('total'))['m']

    context = {
        "fournisseur": fournisseur,
        "commandes": commandes.order_by('-date'),
        "nb_en_attente": nb_en_attente,
        "nb_validees": nb_validees,
        "nb_refusees": nb_refusees,
        "nb_total": nb_total,
        "montant_total": montant_total,
    }
    return render(request, "dashboard_fournisseur.html", context)

@never_cache
@login_required
def liste_articles(request):
    qs = Article.objects.all().order_by('-stock', 'nom')
    paginator = Paginator(qs, 10)
    page = request.GET.get('page')
    try:
        products = paginator.get_page(page)
    except (EmptyPage, PageNotAnInteger):
        products = paginator.get_page(1)
    return render(request, 'articles.html', {'products': products})

def is_gestionnaire(user):
    return getattr(user, "role", None) in ["gestionnaire", "admin"]

@login_required
@user_passes_test(is_gestionnaire)

def add_product(request):
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.stock = article.quantite
            article.save()
            messages.success(request, "✅ Produit ajouté avec succès.")
            return redirect('articles')
        else:
            messages.error(request, "❌ Formulaire invalide. Veuillez corriger les erreurs.")
    else:
        form = ArticleForm()
    return render(request, 'add_product.html', {'form': form})



@login_required
def delete_product(request, id):
    article = get_object_or_404(Article, id=id)
    if request.method == 'POST':
        article.delete()
        messages.success(request, "Produit supprimé avec succès.")
        return redirect('articles')
    return render(request, 'delete_product.html', {'article': article})




@login_required
def msg(request):
    users = CustomUser.objects.exclude(id=request.user.id)
    return render(request, 'msg.html', {'users': users})


@login_required
def conversation(request, user_id):
    current = request.user
    other = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(sender=current, receiver=other, content=content)
            return redirect('conv', user_id=other.id)
    
    qs = Message.objects.filter(
        (Q(sender=current) & Q(receiver=other)) |
        (Q(sender=other) & Q(receiver=current))
    ).order_by('timestamp')
    
    paginator = Paginator(qs, 10)
    page = request.GET.get('page')
    messages_page = paginator.get_page(page)
    
    return render(request, 'conversation.html', {
        'other_user': other,
        'messages': messages_page,
        'user': request.user
    })
@login_required
def complete_profile(request):
    try:
        if request.method == "GET":
            if request.GET.get("reset"):
                request.session.pop("otp_email", None)
            if "otp_email" in request.session:
                form = OTPVerificationForm()
                return render(request, "complete_profile.html", {
                    "step": "verify",
                    "email": request.session["otp_email"],
                    "form": form
                })
            else:
                form = EmailVerificationForm()
                return render(request, "complete_profile.html", {
                    "step": "email",
                    "form": form
                })

        if "otp_email" not in request.session:
            form = EmailVerificationForm(request.POST)
            print("POST data:", request.POST)
            print("Form is valid? ", form.is_valid())
            print("Form errors:", form.errors)

            if form.is_valid():
                email = form.cleaned_data["email"]
                code_obj = TwoFactorCode.create_code(request.user)
                request.session["otp_email"] = email
                send_mail(
                    subject="Votre code de vérification",
                    message=f"Bonjour {request.user.username},\nVotre code est : {code_obj.code}",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                )
                form_code = OTPVerificationForm()
                return render(request, "complete_profile.html", {
                    "step": "verify",
                    "email": email,
                    "form": form_code
                })
            else:
                return render(request, "complete_profile.html", {
                    "step": "email",
                    "form": form
                })

        email = request.session.get("otp_email")
        form_code = OTPVerificationForm(request.POST)
        if form_code.is_valid():
            code = form_code.cleaned_data["code"]
            try:
                otp = TwoFactorCode.objects.get(user=request.user, code=code, is_used=False)
                if otp.is_valid():
                    otp.is_used = True
                    otp.save()
                    user = request.user
                    user.secondary_email = email
                    user.save()
                    del request.session["otp_email"]
                    messages.success(request,
                        f"L'adresse {email} a bien été ajoutée à votre compte. Vous pourrez vous connecter avec cet email ou celui de l'administrateur.")
                    return redirect("redirect_dashboard")
                else:
                    form_code.add_error("code", "Ce code a expiré.")
            except TwoFactorCode.DoesNotExist:
                form_code.add_error("code", "Code invalide ou déjà utilisé.")

        return render(request, "complete_profile.html", {
            "step": "verify",
            "email": email,
            "form": form_code
        })

    except Exception as e:
        import traceback
        return render(request, "complete_profile.html", {
            "step": "email",
            "form": EmailVerificationForm(),
            "error": traceback.format_exc(),
        })
@login_required


@login_required
def commande_list(request):
    commandes = Commande.objects.filter(employe=request.user)
    return render(request, 'commande_list.html', {'commandes': commandes})

@login_required
def add_commande(request):
    if request.method == "POST":
        form = CommandeForm(request.POST)
        formset = AvoirFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            commande = form.save(commit=False)
            commande.employe = request.user
            commande.save()
            formset.instance = commande
            formset.save()
            messages.success(request, "Commande enregistrée.")
            return redirect('commande_list')
    else:
        form = CommandeForm()
        formset = AvoirFormSet()
    return render(request, 'add_commande.html', {'form': form, 'formset': formset})

@login_required
def commande_detail(request, id):
    commande = get_object_or_404(Commande, id=id)
    avoirs = commande.articles_commande.all()
    return render(request, 'commande_detail.html', {'commande': commande, 'avoirs': avoirs})


def is_gestionnaire(user):
    return user.role in ['gestionnaire', 'admin']


@login_required
@user_passes_test(is_gestionnaire)
def fournisseur_list(request):
    fournisseurs = Fournisseur.objects.all()
    return render(request, 'fournisseur_list.html', {'fournisseurs': fournisseurs})
def add_fournisseur(request):
    if request.method == "POST":
        form = FournisseurUserForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            User = get_user_model()
            user = User.objects.create_user(
                username=data['username'],
                password=data['password'],
                email=data['email'],
                role='fournisseur'
            )
            Fournisseur.objects.create(
                user=user,
                nom=data['nom'],
                contact=data['contact'],
                email=data['email'],
                adresse=data['adresse']
            )
            messages.success(request, "Fournisseur et compte utilisateur créés.")
            return redirect('fournisseur_list')
    else:
        form = FournisseurUserForm()
    return render(request, 'add_fournisseur.html', {'form': form})
@login_required
@user_passes_test(is_gestionnaire)
def edit_fournisseur(request, id):
    fournisseur = get_object_or_404(Fournisseur, id=id)
    if request.method == "POST":
        form = FournisseurForm(request.POST, instance=fournisseur)
        if form.is_valid():
            form.save()
            messages.success(request, "Fournisseur modifié.")
            return redirect('fournisseur_list')
    else:
        form = FournisseurForm(instance=fournisseur)
    return render(request, 'edit_fournisseur.html', {'form': form})

@login_required
@user_passes_test(is_gestionnaire)
def delete_fournisseur(request, id):
    fournisseur = get_object_or_404(Fournisseur, id=id)
    if request.method == "POST":
        fournisseur.delete()
        messages.success(request, "Fournisseur supprimé.")
        return redirect('fournisseur_list')
    return render(request, 'delete_fournisseur.html', {'fournisseur': fournisseur})

@login_required
def stats_articles_par_categorie(request):
    data = (
        Article.objects.values('categorie')
        .annotate(nombre=Count('id'))
        .order_by('-nombre')
    )
    categories = [d['categorie'] or 'Sans catégorie' for d in data]
    quantites = [d['nombre'] for d in data]
    return JsonResponse({'labels': categories, 'data': quantites})

@login_required
def stats_top_articles(request):
    articles = Article.objects.order_by('-quantite')[:10]
    return JsonResponse({
        'labels': [a.nom for a in articles],
        'data': [a.quantite for a in articles]
    })

@login_required
def stats_mouvements_stock(request):
    nb_jours = int(request.GET.get('jours', 7))
    stocks = (
        Stock.objects.filter(date_entree__gte=timezone.now() - timedelta(days=nb_jours))
        .annotate(day=TruncDate('date_entree'))
        .values('day')
        .annotate(entrees=Sum('entree'), sorties=Sum('sortie'))
        .order_by('day')
    )
    labels = [str(x['day']) for x in stocks]
    entrees = [x['entrees'] or 0 for x in stocks]
    sorties = [x['sorties'] or 0 for x in stocks]
    return JsonResponse({'labels': labels, 'entrees': entrees, 'sorties': sorties})

@login_required
def stats_articles_rupture(request):
    rupture = Article.objects.filter(stock__lt=F('stock_min')).count()
    return JsonResponse({'rupture': rupture})

@login_required
def stats_commandes_par_fournisseur(request):
    qs = Fournisseur.objects.annotate(nb=Count('commande')).order_by('-nb')
    return JsonResponse({
        'labels': [f.nom for f in qs],
        'data': [f.nb for f in qs]
    })
from django.shortcuts import render, redirect

from django.conf import settings
from .models import Article

@login_required
def mes_demandes(request):
    demandes = DemandeArticle.objects.filter(employe=request.user)  
    return render(request, 'mes_demandes.html', {'demandes': demandes})


def is_gestionnaire(user):
    return user.role == 'gestionnaire' or user.role == 'admin'
@login_required


@login_required
def faire_demande(request):
    if request.method == 'POST':
        print("====== POST reçu ======")
        print(request.POST)
        form = DemandeArticleForm(request.POST)
        print("Form valid ?", form.is_valid())
        if form.is_valid():
            demande = form.save(commit=False)
            demande.employe = request.user
            demande.save()
            print("Demande créée !", demande)
            messages.success(request, "Demande envoyée avec succès !")
            return redirect('mes_demandes')
        else:
            print("Form errors :", form.errors)
            messages.error(request, "Erreur dans le formulaire.")
    else:
        form = DemandeArticleForm()
    return render(request, 'faire_demande.html', {'form': form})
@login_required
@user_passes_test(is_gestionnaire)
def liste_demandes(request):
    demandes = DemandeArticle.objects.select_related('article', 'employe').order_by('-date_demande')

    statut = request.GET.get('statut')
    if statut:
        demandes = demandes.filter(statut=statut)

    context = {
        "demandes": demandes,
        "statut": statut,
    }
    return render(request, "liste.html", context) 
def export_articles(request, format):
    articles = Article.objects.all()
    search = request.GET.get('search')
    if search:
        articles = articles.filter(nom__icontains=search) | articles.filter(reference__icontains=search)
    
    data = []
    for art in articles:
        data.append({
            "Nom": art.nom,
            "Référence": art.reference,
            "Prix": art.prix,
            "Quantité": art.quantite,
        })
    df = pd.DataFrame(data)

    if format == "excel":
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="articles.xlsx"'
        df.to_excel(response, index=False)
        return response

    elif format == "pdf":
        import io
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
        from reportlab.lib import colors
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer)
        elements = []
        table_data = [df.columns.tolist()] + df.values.tolist()
        t = Table(table_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0d6efd")),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 10),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        elements.append(t)
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="articles.pdf"'
        response.write(pdf)
        return response

    else:
        return HttpResponse("Format inconnu", status=400)
def autocomplete_product_names(request):
    q = request.GET.get('q', '')
    if q:
        results = list(Article.objects.filter(nom__icontains=q).values_list('nom', flat=True)[:10])
    else:
        results = []
    return JsonResponse({'results': results})

def validate_product_field(request):
    if request.method == "POST":
        field_name = list(request.POST.keys())[0]
        value = request.POST[field_name]
        error = ""

        if field_name == "prix":
            try:
                val = float(value)
                if val <= 0:
                    error = "Le prix doit être positif."
            except:
                error = "Prix invalide."
        if field_name == "nom":
            if len(value) < 2:
                error = "Nom trop court."

        return JsonResponse({"error": error})
    return JsonResponse({"error": "Méthode non autorisée."}, status=405)
def decouvrire_demo(request):
    return render(request, 'decouvrire_demo.html')
@login_required
def modifier_quantite(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == "POST":
        form = ArticleUpdateForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            utilisateur = request.user
            if article.stock < article.stock_min:
                email_dest = utilisateur.secondary_email
                if email_dest:
                    sujet = f"⚠️ Stock critique pour « {article.nom} »"
                    corps = (
                        f"Bonjour {utilisateur.username},\n\n"
                        f"Le stock de l'article « {article.nom} » (Réf : {article.reference}) "
                        f"est critique ({article.stock} unités, seuil : {article.stock_min}).\n\n"
                        "Merci de réagir rapidement.\n"
                    )
                    send_mail(
                        sujet,
                        corps,
                        settings.DEFAULT_FROM_EMAIL,
                        [email_dest],
                        fail_silently=False
                    )
            return redirect("liste_articles")
    else:
        form = ArticleUpdateForm(instance=article)

    return render(request, "modifier_article.html", {
        "article": article,
        "form": form
    })

@login_required
def stats_total_articles(request):
    total = Article.objects.count()
    return JsonResponse({'total': total})

@login_required
def stats_fournisseurs_actifs(request):
    date_limite = timezone.now().date() - timedelta(days=30)
    actifs = Fournisseur.objects.filter(
        commande__date__gte=date_limite
    ).distinct().count()
    return JsonResponse({'actifs': actifs})

@login_required
def stats_commandes_en_cours(request):
    en_cours = Commande.objects.filter(
        etat__in=['en_attente', 'en cours']
    ).count()
    return JsonResponse({'en_cours': en_cours})

@login_required
def stats_evolution_stocks(request):
    date_debut = timezone.now().date() - timedelta(days=30)
    
    mouvements = MouvementStock.objects.filter(
        date__date__gte=date_debut
    ).order_by('date__date')
    
    evolution = {}
    date_courante = date_debut
    while date_courante <= timezone.now().date():
        evolution[date_courante.isoformat()] = 0
        date_courante += timedelta(days=1)
    
    for mvt in mouvements:
        date = mvt.date.date().isoformat()
        if mvt.type_mouvement == 'entree':
            evolution[date] += mvt.quantite
        else:
            evolution[date] -= mvt.quantite
    
    return JsonResponse({
        'dates': list(evolution.keys()),
        'variations': list(evolution.values())
    })

@login_required
def stats_delai_livraison(request):
    try:
        date_limite = timezone.now().date() - timedelta(days=90)
        
       
        fournisseurs = Fournisseur.objects.filter(
            commande__date__gte=date_limite
        ).distinct()

        noms_fournisseurs = []
        delais = []

        for fournisseur in fournisseurs:
            noms_fournisseurs.append(fournisseur.nom)
           
            delais.append(4)

       
        if not noms_fournisseurs:
            noms_fournisseurs = ['Aucune donnée']
            delais = [0]

        return JsonResponse({
            'fournisseurs': noms_fournisseurs,
            'delais': delais
        })
    except Exception as e:
        return JsonResponse({
            'fournisseurs': ['Erreur de données'],
            'delais': [0]
        })

@login_required
def stats_stock_minimum(request):
    try:
        articles = Article.objects.filter(stock_min__gt=0)
        
        critique = 0
        attention = 0
        normal = 0
        excedent = 0
        
        for article in articles:
            ratio = article.stock / article.stock_min if article.stock_min > 0 else 0
            
            if ratio < 1:
                critique += 1
            elif ratio < 2:
                attention += 1
            elif ratio < 3:
                normal += 1
            else:
                excedent += 1
        
        total = critique + attention + normal + excedent
        if total == 0:
            return JsonResponse({
                'labels': ['Aucune donnée'],
                'data': [1],
                'colors': ['#e0e0e0']
            })
        
        return JsonResponse({
            'labels': [
                f'Critique (<100%) : {critique} articles',
                f'Attention (100-200%) : {attention} articles',
                f'Normal (200-300%) : {normal} articles',
                f'Excédent (>300%) : {excedent} articles'
            ],
            'data': [critique, attention, normal, excedent],
            'colors': [
                '#dc3545',
                '#ffc107',
                '#28a745',
                '#17a2b8'
            ]
        })
        
    except Exception as e:
        return JsonResponse({
            'labels': ['Erreur de données'],
            'data': [1],
            'colors': ['#dc3545']
        })

@login_required
def stats_impact_co2(request):
    articles = Article.objects.exclude(facteur_co2=0).order_by('-facteur_co2')[:10]
    impact = {
        a.nom: round(a.facteur_co2 * a.stock, 2)
        for a in articles
    }
    
    return JsonResponse({
        'articles': list(impact.keys()),
        'co2': list(impact.values())
    })

@login_required
def stats_total_articles(request):
    total = Article.objects.count()
    return JsonResponse({'total': total})

@login_required
def stats_fournisseurs_actifs(request):
    date_limite = timezone.now().date() - timedelta(days=30)
    actifs = Fournisseur.objects.filter(
        commande__date__gte=date_limite
    ).distinct().count()
    return JsonResponse({'actifs': actifs})

@login_required
def stats_commandes_en_cours(request):
    en_cours = Commande.objects.filter(
        etat__in=['en_attente', 'en cours']
    ).count()
    return JsonResponse({'en_cours': en_cours})

@login_required
def stats_evolution_stocks(request):
    date_debut = timezone.now().date() - timedelta(days=30)
    
    mouvements = MouvementStock.objects.filter(
        date__date__gte=date_debut
    ).order_by('date__date')
    
    evolution = {}
    date_courante = date_debut
    while date_courante <= timezone.now().date():
        evolution[date_courante.isoformat()] = 0
        date_courante += timedelta(days=1)
    
    for mvt in mouvements:
        date = mvt.date.date().isoformat()
        if mvt.type_mouvement == 'entree':
            evolution[date] += mvt.quantite
        else:
            evolution[date] -= mvt.quantite
    
    return JsonResponse({
        'dates': list(evolution.keys()),
        'variations': list(evolution.values())
    })
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from .forms import EntreeStockForm
from .models import MouvementStock
from django.db import connection
def is_gestionnaire(user):
    return user.role in ['gestionnaire', 'admin']
@login_required
def edit_product(request, id):
    article = get_object_or_404(Article, id=id)
    form = ArticleForm(request.POST or None, instance=article)
    if form.is_valid():
        form.save()
        messages.success(request, "Produit modifié avec succès.")
        return redirect('articles   ')
    return render(request, 'edit_product.html', {'form': form, 'article': article})


def nouvelle_entree(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = MouvementStockForm(request.POST)
        if form.is_valid():
            mouvement = form.save(commit=False)
            mouvement.type_mouvement = 'entree'
            article = mouvement.article
            article.stock += mouvement.quantite
            article.save()
            mouvement.save()
            articles = Article.objects.all()
            return render(request, 'articles.html', {'products': articles, 'user': request.user})
        else:
            return HttpResponse('<div class="alert alert-danger">Erreur de saisie.</div>', status=400)
    else:
        form = MouvementStockForm()
    return render(request, 'nouvelle_entree.html', {'form': form})
@user_passes_test(is_gestionnaire)
@login_required
def nouvelle_sortie(request):
    if request.method == "POST":
        form = MouvementStockForm(request.POST)
        if form.is_valid():
            mouvement = form.save(commit=False)
            mouvement.type_mouvement = 'sortie'
            article = mouvement.article
            if article.stock >= mouvement.quantite:
                article.stock -= mouvement.quantite
                article.save()
                mouvement.save()

                if article.stock < 10:
                    user = request.user
                    email_dest = getattr(user, 'secondary_email', None)
                    if email_dest:
                        sujet = f"⚠️ Stock critique pour « {article.nom} »"
                        corps = (
                            f"Bonjour {user.username},\n\n"
                            f"Le stock de l'article « {article.nom} » (Réf : {article.reference}) "
                            f"est critique ({article.stock} unités, seuil d’alerte : 10).\n\n"
                            "Merci de réagir rapidement.\n"
                        )
                        send_mail(
                            sujet,
                            corps,
                            settings.DEFAULT_FROM_EMAIL,
                            [email_dest],
                            fail_silently=False
                        )

                messages.success(request, f"Sortie enregistrée pour {article.nom} (stock : {article.stock})")
                return redirect('articles')
            else:
                messages.error(request, f"Stock insuffisant ! (stock actuel : {article.stock})")
    else:
        form = MouvementStockForm()
    return render(request, "nouvelle_sortie.html", {"form": form})


from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Article
from .utils import generate_openai_report_from_articles




@login_required
@user_passes_test(is_gestionnaire)
def report_ai_view(request):
    articles = Article.objects.all()
    error, rapport_texte = None, ""

    if request.method == "POST":
        try:
            rapport_texte = generate_openai_report_from_articles(articles)
        except Exception as e:
            error = (
                "⚠️ Impossible de générer le rapport IA pour le moment :<br>"
                f"<span style='color:#c00;'>Erreur IA : {e}</span><br>"
                "Merci de vérifier votre abonnement OpenAI ou contactez l'administrateur."
            )
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                "rapport_texte": rapport_texte or "",
                "error": error or ""
            })
    data_summary = [
        f"{art.nom}: Stock={art.stock}, Stock min={art.stock_min}, Rupture={'Oui' if art.stock < art.stock_min else 'Non'}"
        for art in articles
    ]
    return render(request, "openai_report.html", {
        "rapport_texte": rapport_texte,
        "data_summary": data_summary,
        "error": error,
    })
from django.shortcuts import get_object_or_404, redirect

@login_required
@user_passes_test(is_gestionnaire)
def action_demande(request, demande_id, action):
    demande = get_object_or_404(DemandeArticle, id=demande_id)
    if demande.statut == 'en_attente':
        if action == 'approuver':
            demande.statut = 'approuvee'
            demande.save()
        elif action == 'refuser':
            demande.statut = 'refusee'
            demande.save()
    return redirect('liste_demandes')
def is_gestionnaire(user):
    return hasattr(user, 'role') and user.role == 'gestionnaire'

@login_required
@user_passes_test(is_gestionnaire)

def action_demande(request, demande_id, action):
    from .models import DemandeArticle
    from django.shortcuts import get_object_or_404
    if request.method == 'POST':
        demande = get_object_or_404(DemandeArticle, id=demande_id)
        if demande.statut == 'en_attente':
            if action == 'approuver':
                demande.statut = 'approuvee'
            elif action == 'refuser':
                demande.statut = 'refusee'
            demande.save()
            return JsonResponse({'ok': True})
        else:
            return JsonResponse({'ok': False, 'error': "Déjà traité."})
    return JsonResponse({'ok': False, 'error': "Requête invalide."})
