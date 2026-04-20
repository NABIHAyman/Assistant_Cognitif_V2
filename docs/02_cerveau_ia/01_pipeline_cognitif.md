# 🧠 Le Pipeline Cognitif (Pydantic-AI & Model Runner)

Bienvenue dans la salle des machines de l'IA. Tu as réussi à créer un flux de réflexion très structuré. Voyons comment tu as orchestré cela.

## 1. Pydantic-AI : L'Agent Structurant
Normalement, quand on parle à ChatGPT ou Ollama, l'IA répond avec une phrase comme "Bonjour, je pense que cette image montre...". 
C'est inexploitable pour une application informatique !

Tu as configuré `pydantic_ai` (dans `main.py`). Ce framework est là pour transformer un flux de texte bavard en données prévisibles et informatiquement utilisables. 

**Comment ? Grâce aux Modèles (Schemas).**
Tu as défini une classe `ProposalResult`. C'est le "moule". L'IA n'a pas le choix : elle doit remplir ce moule (Titre, Action, Domaine, Markdown, Raisonnement).

## 2. La Force du Prompting et de la Ruse (Le Parseur)
Si tu observes bien ton `main.py` (`JSON_TEMPLATE`), tu as contraint l'IA à répondre avec **exclusivement** du JSON.
Mais les petits modèles locaux comme `gemma4` ou `llama3` sont parfois têtus. Ils ajoutent souvent des "Voici votre réponse :" avant le JSON.

Ici, tu as codé une méthode extrêmement intelligente : `parse_ai_response()`.
Cette fonction découpe le texte, cherche l'accolade d'ouverture `{` et celle de fermeture `}`, et nettoie tout le reste. Résultat ? Ton système ne crashera jamais à cause d'une IA trop bavarde.

## 3. Le Processus en Arrière-plan (Background Batching)
Analyser une image prend du temps (plusieurs secondes). Si tu demandes à FastAPI de le faire immédiatement, l'interface utilisateur va bloquer.

Tu as donc créé une logique asynchrone (Batching) :
- La route `/api/analyze/batch` s'active via les **BackgroundTasks** de FastAPI.
- Elle libère immédiatement le navigateur de l'utilisateur ("C'est lancé, tu peux faire autre chose !").
- Derrière, un script scrute discrètement le dossier `/data/inbox/`, prend les images une par une, demande l'analyse à l'IA, convertit le résultat, le sauvegarde en DB et déplace physiquement l'image dans `/data/archive/` ou `/data/trash/`.

## 4. Docker Model Runner (L'hôte de l'IA)
Où tourne ce fameux modèle ?
Dans ton architecture, tu utilises un hôte Docker. Grâce à la variable `OLLAMA_HOST=http://host.docker.internal:11434`, ton conteneur Backend n'a pas besoin de faire tourner son propre modèle très lourd. Il se connecte en direct à l'Ollama qui tourne nativement sur l'ordinateur. C'est ce qu'on appelle "Déléguer la charge", une excellente pratique DevOps !

---
**💡 Résumé Pédagogique :**
L'IA a besoin de règles strictes. Avec un **Prompt précis**, une contrainte **Pydantic** et un **Nettoyeur de texte** (Parser), tu as transformé un LLM générique en un rouage d'horlogerie prévisible qui travaille tout seul en arrière-plan.

**👉 Prochaine lecture suggérée :** Pour comprendre où vont toutes ces données, rendez-vous dans `../03_architecte_donnees/01_persistance_et_notion.md`.
