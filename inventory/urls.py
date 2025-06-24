# gestiondestock/inventory/urls.py
from .views import msg, conversation 
from django.urls import path


from .views import (
    # Authentification & profil
    home,
    login_view, log_out, redirect_dashboard,
    dashboard_gestionnaire, dashboard_employe, dashboard_admin,
    dashboard_fournisseur, autocomplete_product_names,
    complete_profile,export_articles,

    # Articles
    liste_articles, add_product, edit_product, delete_product,

    commande_detail, commande_list, add_commande,
    fournisseur_list, add_fournisseur, edit_fournisseur, delete_fournisseur,dashboard_fournisseur,report_ai_view,
    # Fournisseurs

    # Messagerie
    msg, conversation,validate_product_field,
    nouvelle_sortie  , nouvelle_entree,faire_demande,mes_demandes,
    
    stats_articles_par_categorie,stats_top_articles,stats_mouvements_stock,
    stats_articles_rupture, stats_commandes_par_fournisseur,render,liste_demandes , decouvrire_demo,
)

urlpatterns = [
    # Authentification
    path('login/',  login_view,         name='login'), 
    path('logout/', log_out, name='log_out'),
    path('', home, name='home'), 
    path('redirect-dashboard/', redirect_dashboard, name='redirect_dashboard'),
    path('dashboard/gest/',  dashboard_gestionnaire, name='dashboard_gestionnaire'),
    path('dashboard/emp/',   dashboard_employe,      name='dashboard_employe'),
    path('dashboard/admin/', dashboard_admin,        name='dashboard_admin'),
    path('dashboard/fournisseur/', dashboard_fournisseur, name='dashboard_fournisseur'),
# inventory/urls.py
    path('profile/complete/', complete_profile, name='complete_profile'),

    #path('profile/success/',  success_view,          name='success_url'),

    # Articles
    path('articles/',             liste_articles,  name='product_list'),
    path('articles/ajouter/',     add_product,     name='add_product'),
    path('articles/<int:id>/edit/',   edit_product,    name='edit_product'),
    path('articles/<int:id>/suppr/',  delete_product,  name='delete_product'),



    path('commandes/', commande_list, name='commande_list'),
    path('commandes/ajouter/', add_commande, name='add_commande'),
    path('commandes/<int:id>/', commande_detail, name='commande_detail'),


    # Messagerie
# Après
    path('messages/', msg, name='msg'),
    path('conv/<int:user_id>/', conversation, name='conv'),
    
    # Rapport IA
    path('report-ai/', report_ai_view, name='report_ai_view'),
    #path('report-ai/', report_ai_view, name='openai_report'),
    path('fournisseurs/', fournisseur_list, name='fournisseur_list'),
    path('fournisseurs/ajouter/', add_fournisseur, name='add_fournisseur'),
    path('fournisseurs/<int:id>/modifier/', edit_fournisseur, name='edit_fournisseur'),
    path('fournisseurs/<int:id>/supprimer/', delete_fournisseur, name='delete_fournisseur'),
    
    # URLs pour statistiques API
    path('stats/articles-par-categorie/', stats_articles_par_categorie, name='stats_articles_par_categorie'),
    path('stats/top-articles/', stats_top_articles, name='stats_top_articles'),
    path('stats/mouvements-stock/', stats_mouvements_stock, name='stats_mouvements_stock'),
    path('stats/articles-rupture/', stats_articles_rupture, name='stats_articles_rupture'),
    path('stats/commandes-par-fournisseur/', stats_commandes_par_fournisseur, name='stats_commandes_par_fournisseur'),

# Page HTML statistiques
    path('statistiques/', lambda r: render(r, "statistique.html"), name="statistique"),
    path('mouvements/entree/', nouvelle_entree, name='nouvelle_entree'),
    path('mouvements/sortie/', nouvelle_sortie, name='nouvelle_sortie'),
    path('employe/demande/', faire_demande, name='faire_demande'),
    path('employe/mes-demandes/', mes_demandes, name='mes_demandes'),
    # inventory/urls.py
    path('demandes/', liste_demandes, name='liste_demandes'),
    path('articles/export/<str:format>/', export_articles, name='export_articles'),
    path('autocomplete-product-names/', autocomplete_product_names, name='autocomplete_product_names'),
    path('articles/validate-field/', validate_product_field, name='validate_product_field'),
    path('decouvrire-demo/', decouvrire_demo, name='decouvrire_demo'),
    
]
