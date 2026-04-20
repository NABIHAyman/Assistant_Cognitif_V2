# 🏗️ L'Architecte des Données (Gestion, Persistance & MCP)

Dans ce parcours, nous enfilons la casquette "Base de données & Intégrations". C'est ici que tu gères comment la mémoire du système est sauvegardée de manière permanente.

## 1. La Mémoire Vive : SQLAlchemy (`models.py`)
Tu as mis en place **SQLAlchemy**, qui est ce qu'on appelle un ORM (Object-Relational Mapping).
Au lieu d'écrire des grosses requêtes SQL compliquées (`INSERT INTO propositions...`), SQLAlchemy te permet de manipuler les lignes de ta base de données comme si c'étaient des objets Python.

Par exemple :
```python
class Proposition(Base):
    __tablename__ = "propositions"
    # ...
```
Dès que l'application s'allume, SQLAlchemy regarde cette classe, et grâce au système de métadonnées, il va automatiquement créer le fichier `cognition.db` (SQLite) avec toutes ses colonnes correspondantes. Simple, propre, et résilient. L'état `status="pending"` est roi ici, et garde tes analyses jusqu'à ce que tu décides de les publier.

## 2. La Mémoire Physique : Les Fichiers (`executor.py`)
Tout ne va pas dans la base de données. Ton système gère une vraie arborescence de fichiers Markdown !
Quand tu cliques sur "Approuver" sur le dashboard, le fichier `executor.py` entre en scène.
- Il prend la structure validée en base de données.
- Il vérifie si le dossier de catégorie (`domain/`) existe, sinon il le crée.
- Il formatte de façon propre un cartouche entête : `📅 Intégré le [date]` et `Tags : [...]`.
- Puis il l'écrit physiquement sur le disque. C'est l'encyclopédie "locale" de l'utilisateur.

## 3. Le Mégaphone : FastMCP et Notion
C'est ta "killer-feature" ! Le Model Context Protocol (MCP).
Tu as un conteneur dédié à ça : `mcp-server`.
L'interface MCP permet une communication standardisée avec le monde extérieur. Au lieu de noyer ton backend principal (`main.py`) avec le code lourd de l'API Notion, tu as séparé les responsabilités.

Que se passe-t-il après l'écriture du Markdown ?
1. Le Backend appelle le Serveur MCP via une transmission en temps réel (SSE - Server-Sent Events).
2. Le Serveur MCP abrite la fonction `upsert_notion_page()`.
3. Le MCP exécute l'action et répond au backend que tout est bon.

**Pourquoi c'est pro ?**
Parce que tu as "Découplé" ton code. Si demain, Notion change d'API, ou si tu veux rajouter l'envoi d'un email récapitulatif, tu toucheras au code du `mcp-server` SANS JAMAIS risquer de casser la logique d'analyse de FastAPI !

---

**💡 Résumé Pédagogique :**
L'information est d'abord **mise en quarantaine** (SQLite). Une fois approuvée, elle est **ancrée localement** (Markdown) et enfin **téléportée à l'extérieur** via un pont standardisé (MCP vers Notion).

**👉 Prochaine lecture suggérée :** Pour comprendre les filets de sécurité et comment tous les environnements communiquent, rendez-vous dans `../04_moteur_devops/01_orchestration_et_resilience.md`.
