# 🛡️ Exceptions et Rotation Temporelle

Niveau 2 des opérations systèmes (DevOps). La tuyauterie fonctionne, mais dans un environnement professionnel (ou pendant 14h de session de code), les cratères, les failles et le stockage sont les plus grands ennemis du développeur.

## 1. Mettre fin au Crash Fatal : Exception Handler
Le serveur `uvicorn` (qui héberge ton FastAPI) stoppe net quand une erreur "Unhandled" (non attrapée) survient violemment dans ton code asynchrone.

Tu as mis en place ce qui s'apparente à des "airbags géants" pour tous les passagers :
```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"💥 CRASH FATAL NON GÉRÉ sur la route {request.url.path}")
    logger.exception(exc)
    return JSONResponse(status_code=500, content={"detail": "Regarde /data/logs/..."})
```

**Anatomie du Crash Intelligent :**
- Peu importe si Pydantic explose, si SQLite se fige ou si une image malicieuse corrompt `PIL`, au lieu d'afficher aux yeux de l'utilisateur "Internal Server Error" binaire...
1. Ton appli re-route l'erreur.
2. Tu écris un marqueur (`request.url.path`) pour savoir QUELLE route l'a provoquée.
3. Tu renvoies proprement la balle au front (JSON 500) pour afficher une pop-up polie dans Vue.js, afin que l'UI ne se bloque pas bêtement.

## 2. Loguru : Oublier la malédiction de `print()`
Quand on débute, on met des `print("ca passe")` partout. Le problème de Docker, c'est que les `print()` vont dans la console virtuelle et se perdent avec la redémarration des conteneurs.

`Loguru` (que tu utilises) est la "Rolex" des Logs Python :
```python
logger.add("/app/data/logs/cognition_backend.log", rotation="10 MB", retention="10 days", level="DEBUG", backtrace=True, diagnose=True)
```

Que signifie cette ligne magistrale qui est invisible mais vitale ?
- **`rotation="10 MB"`** : Les applications mal codées font gonfler leur fichier de log jusqu'à 350 Go et font planter le SSD du serveur (Erreur de débutant numéro 1). Ton application, elle, créera un nouveau fichier log tous les 10 Mo.
- **`retention="10 days"`** : Mieux encore, l'application auto-supprimera les vieux `cognition_backend.log_XXX` dès qu'ils datent de plus de 10 jours. Tu viens de programmer de l'auto-nettoyage serveur naturel. Aucun besoin d'aller effacer les dossiers manuellement.
- **`diagnose=True`** et **`backtrace=True`** : Si ton application crashe, Loguru est configuré pour afficher non seulement VRAIMENT où ça a cassé, mais il inspecte aussi la valeur de de *chaque variable* présente au moment du drame et te l'imprime.

## 3. Host.Docker.Internal (L'Évasion Locale)
Il existe une règle en programmation conteneurisée : *Ce qui se passe dans un conteneur reste dans un conteneur*. Ton API Backend est aveugle : elle ne connait pas ton PC, elle ignore tout de l'extérieur. 

Or, ton `Ollama` tourne natif sur ton PC (localhost:11434). Tu ne l'as pas dockerisé car l'accès aux cartes graphiques y est trop complexe. 
Ton astuce magique : l'utiliser dans la configuration LLM `OLLAMA_HOST=http://host.docker.internal:11434`.
`host.docker.internal` agit comme un "tunnel secret" qui permet au backend de percer le mur du conteneur pour remonter sur ton ordinateur d'origine. C'est l'essence du développement Docker "hybride" (Une appli docker communiquant avec un système propriétaire).

---
**💡 Résumé du palier :**
Ton système ne peut plus s'éteindre à ton insu. S'il coule, avec tes airbags et la mécanique de `loguru`, tu sais très exactement "où, quand, comment, et avec quelles variables" il a touché le fond. Et le système fait même le ménage derrière lui quand tu ne le regardes pas.

**👉 Prochainement :** Nous entrerons directement dans le volume et la virtualisation du disque, comment `/data/` est ponté entre ton bureau et le serveur !
