# 🏦 Migration vers PostgreSQL et Event Sourcing

Pour l'Architecte de Données, ce 5ème chapitre est essentiel si le logiciel devient massif et multi-threading extrême.

## 1. La Limite de SQLite
SQLite (`cognition.db`) est une merveille d'ingénierie. C'est le moteur de base de données le plus déployé au monde.
Mais son point faible structurel est l'"Écriture Concurrente". Si 40 requêtes API veulent insérer des nouvelles propositions à la milliseconde exacte où le "Batch Background" est en train d'enregistrer 120 images, le fichier physique `.db` risque de se "locker" (File Lock), générant l'effrayante erreur `Database is locked`.

## 2. PostgreSQL : L'Artillerie Lourde
Le move classique d'un Cloud Architect pour résoudre cela est de brancher **PostgreSQL**.
Le miracle de ton application ? Vu que tu as utilisé SQLAlchemy (l'ORM), changer d'une base de poche à un mastodonte d'entreprise ne va te prendre que deux lignes :
```python
# Remplacer : "sqlite:////app/data/cognition.db"
# Par : "postgresql://user:pass@db_container:5432/cognitif_db"
```
Tu devras juste ajouter un 4ème conteneur `postgres` dans ton `docker-compose.yml`, et SQLAlchemy recréera toutes tes tables de lui-même. Ton code restera inchangé.

## 3. L'Évolution ultime : Event Sourcing (Journal inaltérable)
Dans le système actuel, quand une proposition "Pending" est corrigée par l'humain et publiée, elle devient "Approved" et son contenu est écrasé.
En architecture financière ou très complexe, on utilise **l'Event Sourcing**.
Plutôt que d'écraser la "Proposition 42" pour changer son statut de `pending` à `approved`, on écrit une **nouvelle ligne** dans une table d'événements :
1. `Event 1` : Proposition_Creée (Contenu X)
2. `Event 2` : Utilisateur_Edite_Proposition (Contenu Y)
3. `Event 3` : Proposition_Approuvée

Cela crée un "Grand Livre de Comptes" et te permet un jour de pouvoir faire un "Rewind" de l'intelligence artificielle pour voir *exactement* ce qu'elle avait proposé face à l'édition d'un utilisateur un mardi d'il y a trois mois !

---
**💡 Vision V3 :** 
Basculer ton ORM SQLAlchemy sur un hubteau Postgres, et passer d'un système où on "met à jour l'info" vers un système où l'on garde une traçabilité totale (Journaling des Événements).
