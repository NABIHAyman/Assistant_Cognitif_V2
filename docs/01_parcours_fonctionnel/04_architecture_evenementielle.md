# ⏱️ L'Illusion de l'Immédiateté : Architecture Événementielle

Bienvenue dans la dernière épopée de ton Parcours Fonctionnel (Niveau 4 - 100%).
Si tu mets un modèle LLM très lourd sur ton ordinateur, une analyse d'image avec vision peut prendre entre 10 et 40 secondes. Pourtant, sur Vue.js, quand l'utilisateur lance le traitement par lot (Batch), l'interface lui dit immédiatement "En cours...". Comment as-tu fait ?

## 1. Non-Blocking I/O (L'accueil rapide)
Tout le secret réside dans cette fonctionnalité de FastAPI appelée `BackgroundTasks` :

```python
@app.post("/api/analyze/batch")
async def trigger_batch_analysis(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_batch_background)
    return {"status": "success", "message": "Batch lancé en arrière-plan."}
```
Si tu avais appelé `await process_batch_background()`, le navigateur web entier serait resté bloqué en mode "Chargement..." pendant 15 minutes (le temps de traiter 30 images). L'utilisateur aurait fini par fermer la page.
Ici, FastAPI confie le travail (la fonction lourde) à un "employé en arrière-plan", et **retourne immédiatement la réponse**. Le navigateur est libéré en 0.05 seconde. C'est l'essence du Web Asynchrone !

## 2. Le Cycle de vie des Dossiers (Inbox -> Archive)
Derrière le rideau, que fait l'employé en arrière-plan ? 
Il boucle inlassablement. Il regarde le dossier `inbox/`.
Ton code gère un véritable **Pipeline de triage physique** :
1. **L'Extraction** : `glob.glob` trouve les `.jpg` et `.png`.
2. **Le Jugement (IA)** : S'il y a du bruit (L'IA estime l'image inutile via `action == "ignore"`), le script le pousse manuellement via `shutil.move` dans `trash/`. 
3. **Le Succès** : Si l'IA trouve du sens, elle classe l'information, et le fichier original part dans `archive/` en guise de sauvegarde inaltérable.

## 3. Le Lien Psychologique avec le Frontend
Comment l'utilisateur sait-il que le batch avance si la connexion HTTP a été coupée après avoir dit "Batch lancé" ?
Il utilise la route du Niveau 3 (`/api/proposals`). Vue.js fait un *Polling* : toutes les X secondes, il vient demander secrètement à SQLite "Hey, combien as-tu de propositions `pending` maintenant ?". L'utilisateur voit alors les propositions apparaître "magiquement" une par une à l'écran, pendant que le serveur travaille en sous-marin.

---
**💡 Le Bilan d'Expert :**
Tu viens de comprendre le **Découplage Temporel**. Un système senior ne force jamais un humain à attendre devant le résultat d'une machine lente. Le Serveur retourne toujours une promesse immédiate ("Je m'en occupe") puis l'humain consulte l'avancement via une "fenêtre vitrée" (Le Polling REST sur la base SQLite). C'est exactement comme cela que les grands SaaS (comme Netflix ou AWS) traitent l'encodage vidéo massivement en tâche de fond !
