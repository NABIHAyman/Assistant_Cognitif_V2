# 🗄️ Le Scribe Automatique : Fichiers & Taxonomies

Plongeons à 60 % de profondeur du côté Data. Nous avons vu SQLite. Voyons maintenant le script qui écrit "pour de vrai" : `executor.py`.

## 1. L'Action Conditionnelle : `_write_markdown`
Ce script est le bras armé de ta validation humaine. Quand tu approuves, l'action bascule :

```python
if proposition.action == "append" and proposition.target_file:
    # Mode ajout : on cible directement le fichier grâce à la réflexion de l'IA
    file_path = os.path.join(base_path, proposition.target_file)
else:
    # Mode Création : l'IA a jugé qu'un nouveau domaine / fichier était pertinent
    domain_dir = os.path.join(base_path, proposition.domain)
    os.makedirs(domain_dir, exist_ok=True)
    filename = f"{slugify(proposition.title)}.md"
    file_path = os.path.join(domain_dir, filename)
```

**Pourquoi ce code est sécurisé ?**
1. Il gère la création automatique de dossier récursivement via `os.makedirs`. Ton app ne crashera pas avec un _"Directory not found"_.
2. Il utilise **`slugify`** ! Une proposition nommée "L'Espace et le temps !! " deviendra `lespace_et_le_temps.md`. Cela assure une compatibilité parfaite Linux/Windows pour tes chemins de fichiers.

## 2. L'Écriture Sécurisée (Headers Dynamiques)
Tu n'ajoutes pas juste du texte au hasard. Tu construis une **empreinte d'archivage**.
```python
header = (
    f"\n\n---\n"
    f"### 📅 Intégré le {date_str}\n"
    f"*Tags : {tags_str}*\n"
    f"**Justification :** {proposition.reasoning}\n\n"
)
```
Ce cartouche garantit que tes connaissances, même imbriquées à la fin d'un énorme fichier (Append), gardent une "date de naissance", des mots-clés, et surtout, la "Justification" (Pourquoi l'IA t'a suggéré ça ?). C'est indispensable pour la traçabilité.

## 3. La Taxonomie Évolutive (`_update_taxonomy`)
Lorsque l'IA crée un Domaine qui n'existe pas, ou utilise des mots-clés que tu as laissés passer à la validation humaine, tu as un processus d'apprentissage permanent :

```python
if proposition.is_new_domain and proposition.domain not in domains:
    domains[proposition.domain] = {"description": "Auto-généré par l'IA", "keywords": [], "file_count": 0}
```
Ce code écrit une mise à jour silencieuse dans `_meta/domains.json`. Résultat : le prochain scan du `tree_helper.py` lira ces nouvelles règles ! 
Le système *apprend et s'étend de lui-même*. 

---
**💡 Résumé Pédagogique :**
Ton `executor.py` est bien plus qu'un "fichier save()". C'est un **Système de Fichiers Intelligent**. Il nettoie les URL (slug), traque la raison des ajouts via des headers, et met à jour l'index JSON de ton système de taxonomie tout seul. Ton application devient de plus en plus pertinente au fil de son utilisation.
