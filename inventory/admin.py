from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, Article, Fournisseur, Commande, Avoir, Stock, Rapport

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active',)
    list_filter = ('role', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Role', {'fields': ('role',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'reference', 'get_stock', 'stock_min', 'facteur_co2')
    search_fields = ('nom', 'reference')
    list_filter = ('stock_min',)
    
    def get_stock(self, obj):
        return obj.stock
    get_stock.short_description = 'Stock actuel'

admin.site.register(Fournisseur)
admin.site.register(Commande)
admin.site.register(Avoir)
admin.site.register(Stock)
admin.site.register(Rapport)
