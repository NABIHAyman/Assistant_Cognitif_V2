# 🏛️ Sessions SQLAlchemy & Dépendances FastAPI

Bienvenue dans le niveau de profondeur 2 pour les données. 30 % plus poussé, focus sur la notion clé des serveurs webs lourds : **L'état des connexions**.

## 1. La Problématique de SQLite vs FastAPI
Dans ton `models.py`, tu utilises une base de données de "poche", robuste mais simple : **SQLite** (`cognition.db`).
Le problème historique de SQLite, c'est qu'il ne supporte pas l'accès asynchrone multithread comme FastAPI le demande avec ses `async def`. FastAPI est une Formule 1 asynchrone qui crée plein de threads. Si deux threads tentent de parler à SQLite en même temps, SQLite panique et bloque le fichier.

**Ta solution est discrète mais critique :**
```python
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
```
Ce `check_same_thread=False` est ta rustine officielle locale. Elle dit à SQLite : "Laisse FastAPI ouvrir la base avec plusieurs threads simultanés, ce sont des amis."

## 2. Le Cycle de vie avec l'Injection de Dépendances (Depends)
Un des concepts les plus puissants que tu as implémentés de façon très propre se trouve à la toute fin de ton `models.py` :
```python
def get_db():
    db = SessionLocal()
    try:
        yield db       # On "prête" la connexion à FastAPI
    finally:
        db.close()     # On raccroche le téléphone
```

**À quoi ça sert ? Au découplage !**
Plutôt que d'ouvrir une session manuellement dans chaque route (ce qu'un junior ferait, en oubliant 9 fois sur 10 de la fermer et en causant un "Memory Leak" ou une saturation de connexions), toi, tu l'utilises en injection.

Dans ta route d'API :
```python
def get_pending_proposals(db: Session = Depends(get_db)):
    proposals = db.query(Proposition).filter(Proposition.status == "pending").all()
```
FastAPI va exécuter `get_db()`.
Dès que la route est finie (erreur, succès ou crash), FastAPI va retourner au `finally` du `get_db()` et **garantira obligatoirement** le `db.close()`.
C'est ça qu'on appelle "Industriel" : la tuyauterie se nettoie toute seule.

## 3. Le Commit vs Add : Les Écluses à Données
Lorsqu'une nouvelle proposition d'IA arrive, tu ne changes pas l'histoire tout de suite :

```python
db.add(nouvelle_proposition)  # 1. On "met en scène" la modification dans la RAM
db.commit()                   # 2. On "verrouille" la modification sur le disque physique
db.refresh(nouvelle_proposition) # 3. On demande la version finale avec son ID auto-généré
```

Cela te permet (dans de futures itérations) de faire de la "Gestion Transactionnelle" : si l'analyse d'un très grand batch d'images échoue en plein milieu, s'il n'y a pas encore eu le `db.commit()`, le système pourra dire "Annuler, rollback !". Aucune donnée ne sera corrompue au milieu.

---
**💡 Ce qu'il faut en retenir :**
Tu viens de comprendre la mécanique d'une ORM (Object-Relational Mapping). Tu es passé d'un monde d'opérations basiques à un monde par **Transactions**.
Ta base de données est protégée contre la saturation via `Depends()` et SQLite est dompté pour une utilisation asynchrone moderne.

**👉 Prochainement :** Nous irons décortiquer l'intérieur du `FastMCP` et la manière d'envoyer tout ça vers Notion avec les outils du SDK !
