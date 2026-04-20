# 🖥️ Le Contrat REST : Dialogue entre Vue.js et FastAPI

Nous voici à 60 % de technicité fonctionnelle. Un frontend et un backend sont deux logiciels distincts qui ne partagent pas la même mémoire. Leur seule façon de se parler, c'est l'API REST.

## 1. La Route de la Découverte (`/api/proposals`)
Imagine que le backend travaille la nuit sur un "Batch" (une file d'attente) de 50 images. Comment le frontend Vue.js le sait-il au matin ?
Vue.js fait un appel GET sur `/api/proposals`. 

La logique backend :
```python
@app.get("/api/proposals")
def get_pending_proposals(db: Session = Depends(get_db)):
    proposals = db.query(Proposition).filter(Proposition.status == "pending").all()
    return {"proposals": [...]} # Structure JSON renvoyée au front
```
Vue.js agit comme un **Viewer d'État**. Il n'a aucune intelligence métier. Il se contente de demander "Qu'est-ce qui est en attente ?" et le backend lui renvoie l'état exact de la table `propositions` filtrée sur `pending`. C'est le principe fondamental de **Stateless REST**.

## 2. L'Action Décisive (`/api/publish/{prop_id}`)
Quand l'utilisateur a relu l'analyse de l'IA (le titre, les tags, le contenu markdown) sur son interface Vue.js, il peut éditer les champs directement (si l'IA s'est trompée sur un tag par exemple).

Au clic sur "Publier", Vue.js prépare un **Payload** (un paquet cadeau de données) :
```javascript
// Côté Vue.js (conceptuel)
fetch(`/api/publish/${prop_id}`, {
  method: "POST",
  body: JSON.stringify({
    title: "Nouveau titre corrigé",
    tags: "tag1,tag2"
  })
})
```

Et le Backend réagit via `Body({})` pour écraser les données avant publication :
```python
@app.post("/api/publish/{prop_id}")
async def publish_proposal(prop_id: int, payload: dict = Body({}), db: Session = Depends(get_db)):
    proposition = db.query(Proposition).filter(Proposition.id == prop_id).first()
    # On force la correction humaine sur la proposition IA :
    if payload:
         proposition.title = payload.get("title", proposition.title)
    # ... puis _write_markdown(), puis _call_mcp_notion()
```

## 3. Le Super-Pouvoir : La Single Source of Truth
Si tu observes bien, la route `/publish` reçoit le payload, **écrase** les erreurs de l'IA par tes corrections humaines, puis appelle `_write_markdown` et MCP. 
**Ta correction est donc propagée absolument partout en une seule fois :**
1. Mise à jour de la Base de Donnée SQLite.
2. Écriture du fichier Markdown physique corrigé.
3. Envoi à Notion corrigé.

---
**💡 Résumé Pédagogique :**
L'interface Vue.js n'édite jamais les fichiers ni Notion directement. Elle agit comme une **télécommande de télévision** (via HTTP). C'est le Backend (la télévision) qui reçoit l'ordre, modifie ses circuits internes, et projette le résultat partout pour garder une intégrité parfaite. C'est l'essence de l'architecture Client-Serveur 3-tiers.
