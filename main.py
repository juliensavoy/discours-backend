from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI
import smtplib
from email.message import EmailMessage
import os
from notion_client import Client

def envoyer_discours(destinataire: str, contenu: str):
    msg = EmailMessage()
    msg["Subject"] = "Votre discours de mariage complet 💍"
    msg["From"] = os.getenv("EMAIL_FROM")  # ton adresse
    msg["To"] = destinataire
    msg.set_content(contenu)

    with smtplib.SMTP_SSL("mail.infomaniak.com", 465) as smtp:
        smtp.login(os.getenv("EMAIL_FROM"), os.getenv("EMAIL_PASSWORD"))
        smtp.send_message(msg)



load_dotenv()

app = FastAPI()

# Autoriser les requêtes depuis le frontend (Astro)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is missing")

client = OpenAI(api_key=api_key)

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")


def log_to_notion(
    discours: str,
    prenom: str,
    marie: str,
    partenaire: str,
    style: str,
    lien: str,
    rencontre: str,
    qualites: str,
    anecdotes: str,
    souvenir: str,
    duree: str,
):
    try:
        notion = Client(auth=NOTION_TOKEN)
        properties = {
            "Discours": {"title": [{"text": {"content": discours or ""}}]},
            "Prénom": {"rich_text": [{"text": {"content": prenom or ""}}]},
            "Marié": {"rich_text": [{"text": {"content": marie or ""}}]},
            "Partenaire": {"rich_text": [{"text": {"content": partenaire or ""}}]},
            "Style": {"rich_text": [{"text": {"content": style or ""}}]},
            "Lien": {"rich_text": [{"text": {"content": lien or ""}}]},
            "Rencontre": {"rich_text": [{"text": {"content": rencontre or ""}}]},
            "Qualités": {"rich_text": [{"text": {"content": qualites or ""}}]},
            "Anecdotes": {"rich_text": [{"text": {"content": anecdotes or ""}}]},
            "Souvenirs": {"rich_text": [{"text": {"content": souvenir or ""}}]},
            "Durée": {"rich_text": [{"text": {"content": duree or ""}}]},
        }
        notion.pages.create(parent={"database_id": NOTION_DATABASE_ID}, properties=properties)
    except Exception:
        pass


@app.post("/generate")
async def generate_speech(
    prenom: str = Form(...),
    marie: str = Form(...),
    partenaire: str = Form(...),
    lien: str = Form(...),
    style: str = Form(None),
    qualites: str = Form(None),
    anecdotes: str = Form(None),
    souvenir: str = Form(None),
    rencontre: str = Form(None),
    duree: str = Form(None),
):
    prompt_parts = [
        f"Tu es une intelligence artificielle chargée d’écrire un discours de mariage personnalisé.",
        f"La personne qui parle s'appelle {prenom}, et fait un discours pour {marie}, qui se marie avec {partenaire}.",
        f"Son lien avec les mariés est : {lien}.",
    ]

    if style:
        prompt_parts.append(f"Le style du discours doit être {style}.")
    if rencontre:
        prompt_parts.append(f"Ils se sont rencontrés de la manière suivante : {rencontre}.")
    if qualites:
        prompt_parts.append(f"Voici les qualités du ou de la marié(e) : {qualites}.")
    if anecdotes:
        prompt_parts.append(f"Inclus l’anecdote suivante dans le discours : {anecdotes}.")
    if souvenir:
        prompt_parts.append(f"Voici un souvenir important à mentionner : {souvenir}.")
    if duree:
        prompt_parts.append(f"Le discours doit durer environ {duree}.")

    prompt_parts.append("Rédige un discours naturel, fluide, adapté à un mariage.")

    final_prompt = " ".join(prompt_parts)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": final_prompt}],
        max_tokens=1000
    )

    speech = response.choices[0].message.content
    # Log to Notion (erreur silencieuse)
    log_to_notion(
        discours=speech,
        prenom=prenom,
        marie=marie,
        partenaire=partenaire,
        style=style or "",
        lien=lien,
        rencontre=rencontre or "",
        qualites=qualites or "",
        anecdotes=anecdotes or "",
        souvenir=souvenir or "",
        duree=duree or "",
    )
    return {"speech": speech}

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


@app.post("/send-discours")
async def send_discours(email: str = Form(...), discours: str = Form(...)):
    if not EMAIL_FROM or not EMAIL_PASSWORD:
        return {"status": "error", "message": "Configuration e-mail manquante"}

    msg = EmailMessage()
    msg["Subject"] = "Votre discours de mariage complet 💍"
    msg["From"] = EMAIL_FROM
    msg["To"] = email
    msg.set_content(discours)

    try:
        with smtplib.SMTP_SSL("mail.infomaniak.com", 465) as smtp:
            smtp.login(EMAIL_FROM, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return {"status": "success", "message": "Email envoyé"}
    except Exception as e:
        return {"status": "error", "message": str(e)}