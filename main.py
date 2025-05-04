from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Autoriser les requêtes depuis le frontend (Astro)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

    return {"speech": response.choices[0].message.content}
