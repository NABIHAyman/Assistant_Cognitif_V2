# 🚀 L'Évolution Fonctionnelle : Multi-Utilisateurs & JWT

Bienvenue dans l'Épilogue (Niveau 5). Nous avons couvert 100 % du code actuel. Ce chapitre explore l'avenir : comment transformer cet outil personnel en un véritable SaaS (Software as a Service) Scalable ? 

## 1. La Limite Actuelle : L'Utilisateur Unique
Aujourd'hui, si tu donnes l'URL de ton UI à un ami, vous verrez tous les deux les mêmes propositions dans la liste "Pending". Il n'y a pas de notion de "Propriété". Quiconque clique sur "Approuver" valide l'action pour tout le système.

## 2. Le Saut Vers L'Authentification (JWT)
Le Parcours Fonctionnel V3 (ou SaaS) imposera une barrière à l'entrée sur Vue.js.
Le standard absolu de l'industrie pour les API REST est le **JSON Web Token (JWT)**.
- Lorsqu'un utilisateur se connecte, FastAPI lui signe un passeport (le token) crypté.
- L'utilisateur range ce passeport dans son navigateur (Local Storage ou Cookie HTTP Only).
- À chaque appel API (ex: `/api/proposals`), Vue.js insère le token dans le "Header Authorization".

## 3. L'Impact sur la Route `/publish`
Tu devras modifier FastAPI pour utiliser des dépendances de sécurité :
```python
@app.post("/api/publish/{prop_id}")
async def publish_proposal(
    prop_id: int, 
    current_user: User = Depends(get_current_active_user), # 👈 Le passeport !
    db: Session = Depends(get_db)
):
    # Logique conditionnelle métier :
    if proposition.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Tu n'es pas propriétaire de ce document.")
```

---
**💡 Vision V3 :** 
En ajoutant une table "Utilisateurs" dans ta base de données et un système de JWT, l'interface Vue.js passera d'un "Panneau de Contrôle Central Administratif" à un "Espace Personnel Sécurisé". Ton application sera prête à accueillir mille utilisateurs simultanément.
