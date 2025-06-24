# carbone/views.py
from django.shortcuts import render
import plotly.graph_objs as go
import plotly.offline as opy     
import pandas as pd
from inventory.models import Article
from django.contrib.auth.decorators import login_required, user_passes_test

def is_gestionnaire(user):
    return getattr(user, "role", None) in ["gestionnaire", "admin"]

@login_required
@user_passes_test(is_gestionnaire)
def dashboard_carbone(request):
    articles = Article.objects.all()
    data = []
    for art in articles:
        try:
            facteur = float(getattr(art, "facteur_co2", 0))
            quantite = float(art.quantite)
        except (TypeError, ValueError):
            facteur = 0
            quantite = 0
        empreinte = quantite * facteur
        data.append({"nom": art.nom, "empreinte": round(empreinte, 3), "quantite": quantite})

    df = pd.DataFrame(data)
    if not df.empty and df["empreinte"].sum() > 0:
        fig = go.Figure(data=[
            go.Bar(
                x=df['nom'],
                y=df['empreinte'],
                marker=dict(color="#49cc90"),
                text=df['empreinte'],
                textposition="auto"
            )
        ])
        fig.update_layout(
            title="Empreinte Carbone des Articles (kg CO₂)",
            plot_bgcolor="#222426",
            paper_bgcolor="#222426",
            font_color="#fff"
        )
        graph_div = opy.plot(fig, auto_open=False, output_type='div')
    else:
        graph_div = "<div style='text-align:center;color:#b8bcc2;font-size:1.2rem;margin:2.5rem'>Aucune donnée carbone disponible.<br>Ajoutez des articles et leur facteur CO₂ pour visualiser les statistiques.</div>"

    return render(request, "dashboard.html", {"graph_div": graph_div})
