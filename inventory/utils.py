import openai
from django.conf import settings

def generate_openai_report_from_articles(
    articles,
    model="gpt-3.5-turbo",
    max_tokens=350,
    temperature=0.2
):
    api_key = getattr(settings, "OPENAI_API_KEY", None)
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY non défini dans les settings.")
    client = openai.OpenAI(api_key=api_key)
    lines = [f"{a.nom} | Stock={a.stock} | Min={a.stock_min}" for a in articles]
    prompt = (
        "Tu es expert en gestion de stock international. Voici des articles :\n"
        + "\n".join(lines) +
        "\n\nDonne-moi :"
        "\n- Les 2 plus gros risques (rupture, surstock) en les comparant à la norme mondiale,"
        "\n- 2 indicateurs de performance à surveiller,"
        "\n- 2 actions concrètes pour améliorer la gestion,"
        "\nEn 150 mots max, en français, sous forme de liste à puces, style rapport pro."
        ""
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Assistant IA gestion stock, style rapport pro, français."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


generate_report = generate_openai_report_from_articles
