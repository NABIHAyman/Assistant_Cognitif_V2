# ⚙️ Le Moteur DevOps (Orchestration et Résilience)

Voici notre dernier arrêt ! Le code est beau, les données circulent, l'IA est intelligente... mais comment tout ça tourne ensemble, 24/7, sans imploser ? C'est le rôle de l'Architecte DevOps.

## 1. L'Orchestration avec Docker Compose
Un ordinateur ("Host") peut abriter plusieurs programmes, mais ils ont la fâcheuse manie de se marcher sur les pieds (conflit de ports, de versions de Python, etc.). 
Pour résoudre ça, tu as utilisé Docker.

Ton `docker-compose.yml` est le plan de la ville :
- Il a bâti **3 maisons étanches** (les conteneurs) : `frontend`, `backend` et `mcp-server`.
- Il leur a donné la possibilité de discuter grâce au réseau privé qu'il a créé : le `cognitif_net`.
- C'est ce réseau qui permet au backend d'appeler `http://cognitif_mcp:8000` (le nom de la maison, sans avoir à connaître son IP).

## 2. Éviter les Embouteillages (Ports)
Sur une machine où tu fais beaucoup de développement (comme ton ordinateur où il y a eu Wexia, GitDock, Supabase...), tout le monde veut des ports connus (3000, 8000).
Tu as géré ce casse-tête avec brio : 
- Le Frontend map son port interne sur le `3333` public.
- Le Backend sur le `8020`.
- Le MCP sur le `8021`.
Ainsi, ton projet `Cognitif V2` est pacifique : il ne fera jamais planter tes autres applications en cours de route.

## 3. La Résilience (Healthcheck et Boucliers)
Dans ton `main.py`, tu as glissé plusieurs pépites de production :
- **Le Bouclier Anti-Proxy :** Forcer les proxy HTTP à ignorer les réseaux locaux de Docker. (Très inspiré du monde de l'entreprise où les VPN et Proxies font planter le réseau sans prévenir).
- **L'ExceptionHandler Global :** `@app.exception_handler(Exception)`. Si une variable crashe, ou si le disque est plein, FastAPI aurait normalement cassé secrètement. Là, tu attrapes le moindre débris volant.
- **Loguru (La Boîte Noire Infatigable) :** Tu as retiré les logs par défaut souvent illisibles pour utiliser `loguru`. Mieux, tu les envoies dans `/data/logs/cognition_backend.log` avec l'option `rotation="10 MB"`. Ton serveur ne crashera d'ailleurs plus jamais parce que le disque dur est plein de textes de log : une vraie démarche de sénior.

---

**💡 Résumé Pédagogique :**
Tu as construit des murs étanches (Conteneurs Docker), tu as tracé des autoroutes privées (Reseau Bridge) et tu as ajouté des AirBags (Exception handling) ainsi qu'une belle Boîte Noire (Loguru) pour analyser les vols qui se passent mal.

C'est ce qui fait la différence entre "un script qui marche sur un PC" et "une infrastructure robuste qui peut tourner pendant des mois sans la moindre intervention". 

---

**🎉 Félicitations :** Tu viens de redécouvrir ta propre architecture à 360° ! 
Ces bases solides (Vue ➡️ FastAPI ➡️ Pydantic-AI ➡️ SQLAlchemy ➡️ Docker ➡️ Notion-MCP) te permettront d'étendre la logique Cognitif à l'infini.
