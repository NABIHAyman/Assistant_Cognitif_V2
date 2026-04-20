# 🗺️ Le Voyage de la Donnée (Parcours Fonctionnel)

Bienvenue dans la première étape de notre visite ! Ici, tu vas comprendre le cycle de vie de l'application : qu'est-ce qui se passe quand l'utilisateur clique sur "Analyser une image" ?

On va suivre la donnée (l'image) du début à la fin, sans entrer dans le jargon technique profond.

## 1. Le Point de Départ : L'Interface (Vue.js)
Tout commence dans le navigateur de l'utilisateur. Le frontend (développé en Vue.js avec Tailwind CSS) permet de télécharger une image.
Lorsqu'elle est soumise, le frontend fait un appel réseau (requête HTTP) vers notre backend.

## 2. L'Accueil par le Serveur : L'API FastAPI
L'image atterrit dans le fichier `backend/app/main.py`. C'est le chef d'orchestre de notre application. 
Il a une porte d'entrée spécifique pour les images : la route `/api/analyze`.

Que fait FastAPI ?
1. Il vérifie que c'est bien une image.
2. Il la redimensionne et l'optimise (format WEBP) pour ne pas envoyer des fichiers trop lourds.
3. Il prépare le contexte : il lit ce que le système sait déjà (dans `/data/knowledge-base`).

## 3. L'Intelligence Artificielle : L'Analyse
C'est ici qu'intervient l'Agent. Le backend envoie notre image optimisée (avec le contexte) au "Cerveau" (notre modèle local géré via Ollama).
L'IA la regarde et renvoie une suggestion au format texte brut, qui est une intention ("Il faut classer cette image dans le dossier X").

## 4. Le Décryptage : Du texte à la Structure
La réponse de l'IA est un peu brute. Donc, notre application la nettoie et la vérifie. 
Le résultat est transformé en un "Objet métier" très carré, qu'on appelle une `Proposition`.
*(On verra l'agent en détail dans le parcours "Cerveau IA").*

## 5. L'Enregistrement : Mettre en Attente
Une fois la proposition générée, elle ne va pas tout de suite dans notre base de connaissances ou sur Notion. 
Elle est d'abord sauvegardée dans la base de données SQLite (gérée par SQLAlchemy) avec le statut `pending` (En attente).

## 6. L'Action de l'Utilisateur : L'Approbation
La proposition s'affiche sur le dashboard. L'utilisateur la lit et clique sur **"Approuver"**.
Quand ce bouton est cliqué, on réveille la route `/api/publish`. 
C'est là que l'action finale s'exécute :
- Le texte est enregistré physiquement dans le dossier `data/knowledge-base` (via `executor.py`).
- Le statut passe à `approved`.
- Un signal est envoyé au serveur MCP pour mettre à jour automatiquement **Notion**.

---
**💡 Résumé du Flux :**
`Vue.js (Image)` ➡️ `FastAPI (Optimisation)` ➡️ `Ollama (Analyse)` ➡️ `Pydantic (Structuration)` ➡️ `SQLite (Attente)` ➡️ `Dashboard (Validation)` ➡️ `Fichiers + Notion (Succès)`.

**👉 Prochaine lecture suggérée :** Pour comprendre exactement comment le cerveau fonctionne, rendez-vous dans `../02_cerveau_ia/01_pipeline_cognitif.md`.
