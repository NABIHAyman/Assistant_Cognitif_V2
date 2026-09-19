# Créer la base « Cognition Memory » avec Notion AI

Alternative au script `create_notion_database.py`, sans Python ni clé d'API pour
la création. Copier le prompt ci-dessous dans Notion AI, puis vérifier le
résultat avec la liste en fin de page.

La structure décrite est celle de `cognition_memory.schema.json`.

## Prompt

```text
Crée dans mon espace Notion une base de données pleine page vide nommée exactement :

🧠 Cognition Memory

Ne crée pas une simple page de texte. Je veux une véritable base de données Notion exploitable par une application externe.

Respecte exactement les règles suivantes :

1. Propriétés

La base doit contenir uniquement ces trois propriétés :

- Title
  - Type : Title
  - C'est la propriété titre principale.
  - Nom exact : Title

- Tags
  - Type : Multi-select
  - Nom exact : Tags
  - Crée exactement les options suivantes :
    inspiration_visuelle, contexte_humain, design_narratif, design_patterns, résilience,
    microservices, architecture, film, davidlynch, mystère, cinema, art, peinture,
    reference_inspiration, a_classifier, contexte_industrie, evenement, série, crime,
    télévision, recommendation, bigdata, scalabilite, databases, designpatterns,
    algorithmes, structures_de_donnees, entretien_technique, recrutement,
    software_engineering, structures_de_données, philosophie, existentialisme,
    réflexion_personnelle

- Status
  - Type : Select, et non Status
  - Nom exact : Status
  - Crée une seule option : Approved

N'ajoute aucune autre propriété : pas de Date, URL, Created time, Last edited time, Relation, Formula ou Checkbox.

2. Vues

Crée les trois vues suivantes, si les fonctionnalités disponibles le permettent :

- Table : type Table, nom exact « Table », propriétés affichées : Title, Tags, Status
- Cards : type Gallery, nom exact « Cards », propriétés affichées : Title, Tags, Status,
  taille des cartes : Large, couverture : contenu de la page, cartes sans image conservées
- Reading list : type List, nom exact « Reading list », propriétés affichées : Title, Tags, Status

3. État initial

La base doit être vide. Ne crée aucune fiche d'exemple et n'ajoute aucun texte explicatif dans les pages.

4. Vérification

Après la création, vérifie :
- que le nom de la base est exactement « 🧠 Cognition Memory » ;
- que la propriété principale s'appelle exactement « Title » ;
- que « Tags » est bien une propriété Multi-select ;
- que « Status » est bien une propriété Select ;
- que l'unique valeur de Status est « Approved » ;
- qu'aucune propriété supplémentaire n'a été ajoutée ;
- que les trois vues demandées existent.

Si tu ne peux pas effectuer une partie de cette configuration, ne la remplace pas par une approximation. Indique précisément ce qui reste à faire manuellement.
```

## Vérifier le résultat

Notion AI peut s'écarter du prompt. Dans les paramètres de la base, contrôler que :

- `Status` est de type **Select** (et non Status) avec l'option `Approved` ;
- `Tags` est de type **Multi-select** ;
- la base est une base **pleine page**, pas une page contenant une base.

Le connecteur reste tolérant : il trouve la propriété titre quel que soit son nom
et ne remplit `Tags` et `Status` que s'ils existent avec un type compatible.

## Ensuite

1. Partager la base avec l'intégration Notion (menu « ⋯ » › *Connections*).
2. Copier l'ID de la base (32 caractères de son URL) dans `NOTION_DATABASE_ID`,
   dans `mcp-server/.env`.
3. Redémarrer le connecteur : `docker compose restart mcp-server`.
