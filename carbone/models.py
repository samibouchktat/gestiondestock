# carbone/models.py

from django.db import models
from inventory.models import Article  # Liaison directe avec inventory

class EmissionArticle(models.Model):
    article = models.OneToOneField(Article, on_delete=models.CASCADE, related_name='carbone_info')
    # inventory/models.py
    facteur_co2 = models.FloatField(null=True, blank=True, default=0)
    source = models.CharField(max_length=100, default="ADEME")

    def total_empreinte(self):
        return float(self.article.quantite) * float(self.facteur_co2)
