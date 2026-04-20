# Implémentation du Batch Upload (Drag-and-Drop multiple)

## Contexte
La fonctionnalité MVP permettait un traitement par analyse asynchrone (Batch) du côté Backend. Cependant, l'interface web (Vue.js) n'autorisait le glisser-déposer que d'un seul fichier à la fois, le reste étant ignoré.

## Ce qui a été fait

### 1. Ajout de la route d'Upload dans l'API (`main.py`)
Mise en place de `POST /api/upload/inbox` :
- Reçoit un tableau de fichiers `list[UploadFile]`.
- Enregistre physiquement les fichiers dans le dossier serveur `/app/data/inbox`.
- Prépare le terrain pour que le daemon d'Ollama prenne le relai.

### 2. Ajout de la Dropzone Batch dans Vue.js (`App.vue`)
- Création d'une **seconde zone de drop** (visuellement distincte) sous la zone principale, dédiée à l'upload multiple.
- Récupération intégrale de la boucle de données `event.dataTransfer.files`.
- Envoi vers `/api/upload/inbox`.
- Une fois les fichiers stockés dans l'inbox avec succès, un appel asynchrone "Fire-and-Forget" est fait à `/api/analyze/batch` pour déclencher les `BackgroundTasks` du système, le tout accompagné d'une petite alerte informative.

## La question du dimensionnement (Résolution 1200px et WebP) et le Batching
L'optimisation des images **n'a pas été modifiée ni déplacée**. Elle reste garantie par la fonction `process_batch_background()` existante du backend :
- Au moment précis où la "Background Task" saisit une image dans l'inbox, elle l'ouvre, applique `thumbnail((1200, 1200))`, et la convertit en **WEBP** _avant_ de l'envoyer à l'agent Pydantic-AI. 
- La compression WebP 1200px est donc **totalement respectée** pour le lot entier et s'applique exactement comme pour un upload unique.

## Protection de la ressource locale (Ollama LLM)
Un enjeu majeur lors du glisser-déposer de plusieurs images (ex: 5 à 10 fichiers) était de ne pas envoyer un DDoS accidentel vers le backend Ollama local (qui crasherait immédiatement par manque de VRAM en tentant de traiter 5 requêtes Ollama parallèles).
- En conservant le système mis en place via les notifications UI et la route asynchrone, le traitement IA reste **strictement séquentiel**. 
- Ollama traitera la première image de l'inbox, nettoiera sa mémoire, puis passera logiquement à la suivante, assurant une parfaite rentabilité du pipeline sans aucun crash. L'utilisateur lui, a déjà le retour Web et le navigateur reste pur et débloqué.
