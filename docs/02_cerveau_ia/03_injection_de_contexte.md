# 📡 Conscience de Soi : L'Architecture RAG Dynamique

Nous voici à 60 % de technicité IA. Comment empêcher l'IA d'inventer des catégories qui n'existent pas ou de recréer 10 fois le même fichier avec des noms légèrement différents ? 
**Réponse : Le RAG (Retrieval-Augmented Generation)**. Mais ici, appliqué à une arborescence de fichiers !

## 1. La Conscience de la Taxonomie
L'IA a un syndrome : elle veut tout bien faire. Si tu lui montres une image d'un code Python, elle va suggérer le dossier "Python". Le lendemain, elle suggèrera "programmation", puis "python_scripts". Résultat : une base de données chaotique.

Dans ton `app/utils/tree_helper.py`, la fonction `get_knowledge_context` charge d'abord **`_meta/domains.json`** :
```python
with open(meta_path, "r", encoding="utf-8") as f:
    taxonomy = f.read()
# On crée le bloc "--- TAXONOMIE (DOMAINES ET TAGS AUTORISÉS) ---"
```
Quand tu envoies l'image à Pydantic-AI, il a donc accès au "Règlement Intérieur". Il voit que le dossier "python" existe déjà et a des mots-clés précis associés. Il choisira de s'y ranger plutôt que d'en inventer un nouveau.

## 2. La Conscience Spatiale (Le Scan `os.walk`)
La partie la plus critique de ton prompt engineering est dynamique. Au moment de l'upload, `tree_helper.py` va scanner ton dossier `/app/data/knowledge-base/` de manière récursive.

Il construit virtuellement un arbre (Tree) en texte pour le GPT :
```text
  📂 tech/
    📄 tech/backend.md
    📄 tech/api_rest.md
```
Pourquoi c'est un coup de génie ? 
Regarde cette ligne du code originel : `rel_path = os.path.join(rel_dir, f).replace("\\", "/")`
Tu forces le système à donner **le chemin relatif exact** (ex: `tech/backend.md`) à l'IA.

## 3. Le Pilote Automatique : "Append" vs "Create"
Le prompt stipule à l'IA : "Si tu dois rajouter l'information dans un fichier existant, renvoie l'action 'append' avec le `target_file` depuis l'arbre fourni".

Puisque l'IA a reçu l'arborescence exacte, elle va renvoyer `{"action": "append", "target_file": "tech/backend.md"}` sans aucune faute de frappe ! 

---

**💡 Résumé Pédagogique :**
Sans `get_knowledge_context`, ton IA serait un amnésique travaillant les yeux bandés : elle créerait de nouveaux fichiers à chaque upload. 
Grâce à ce composant, l'IA "lit l'index du livre" avant d'écrire son paragraphe. C'est un cas d'usage extrêmement élégant d'**Injection de Contexte**, le cœur même des intelligences artificielles privées et sécurisées.
