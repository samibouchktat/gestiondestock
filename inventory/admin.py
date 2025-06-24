from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, Article, Fournisseur, Commande, Avoir, Stock, Rapport

# --- 1) Enregistrement de CustomUser via @admin.register ---

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = (
        "username",
        "email",
        "secondary_email",
        "role",
        "is_staff",
        "is_active",
    )

    fieldsets = UserAdmin.fieldsets + (
        (_("E-mail secondaire (2FA)"), {
            "fields": ("secondary_email",),
        }),
        (_("Rôle de l'utilisateur"), {
            "fields": ("role",),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (_("E-mail secondaire (2FA)"), {
            "classes": ("wide",),
            "fields": ("secondary_email",),
        }),
        (_("Rôle de l'utilisateur"), {
            "classes": ("wide",),
            "fields": ("role",),
        }),
    )

    search_fields = ("username", "email", "secondary_email")
    list_filter = ("is_staff", "is_active", "role")


# --- 2) Enregistrements des autres modèles ---
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("nom", "quantite", "facteur_co2")
    search_fields = ("nom",)


admin.site.register(Fournisseur)
admin.site.register(Commande)
admin.site.register(Avoir)
admin.site.register(Stock)
admin.site.register(Rapport)
