# 🐳 Étage 1 : La Philosophie de l'Isolation et du Docker Compose

Si ce projet est présenté dans le cadre d'un module "Docker", il est vital de justifier *pourquoi* ce merveilleux outil est la clé de voûte de ton architecture. Ce fichier est le premier "Étage" de présentation de tes choix DevOps.

## 1. Le Cauchemar du "Ça marche sur ma machine !"
Auparavant, pour que ton application Cognitif soit installée sur l'ordinateur d'un professeur ou d'un collègue, il aurait fallu :
1. Installer Python 3.11 (et espérer qu'il n'ait pas de conflit avec son Python 3.8 existant).
2. Vérifier qu'il a NodeJS v22 installé.
3. Croiser les doigts pour que la version SQLite de son OS soit compatible.
4. Lancer manuellement 3 fenêtres de terminaux différentes.

Ton projet résout ce cauchemar séculaire. Grâce à la conteneurisation, tu as packagé **l'environnement de l'ordinateur** avec le code lui-même.

## 2. L'Architecture en 3 Maisons (Microservices)
Plutôt que de faire un immense bloc "Monolithe" instable, le fichier `docker-compose.yml` construit ton application comme une ville avec 3 maisons séparées :

*   **`frontend`** : Une fois construit, ce conteneur ne contient QUE le strict nécessaire pour héberger le site Vue.js (Un serveur Nginx très léger).
*   **`backend`** : Un environnement Python isolé dédié exclusivement au calcul IA (FastAPI / Pydantic). S'il sature sa propre RAM virtuelle, il explose tout seul, *sans faire tomber le reste du projet*.
*   **`mcp-server`** : Le connecteur Notion est gardé volontairement dans sa propre sphère, limitant ainsi la fuite de la variable secrète `NOTION_API_KEY`.

L'idée fondamentale de Docker ici, c'est **le Découplage**. Ton application n'est plus un gros logiciel, c'est un essaim de mini-programmes spécialisés appelés "Microservices".

## 3. La Simplicité d'Orchestration
La véritable beauté réside dans le mot de passe final :
```bash
docker-compose up --build -d
```
Cette simple commande lit ton plan (`yaml`) et :
1. Démarre un réseau local secret reliant les 3 maisons.
2. Établit l'ordre de démarrage (Le frontend attend via `depends_on: backend`).
3. Monte l'application silencieusement en arrière-plan (`-d`).

---

**💡 Pour ton module Docker :**
Cet étage 1 sert à démontrer que l'orchestration avec `docker-compose` n'a pas été choisie "pour faire joli". Elle a été choisie pour offrir **de la haute portabilité** (Zero Installation requise à part Docker) et du **découplage sécurisé** (Si Notion crashe, ton backend continue de cataloguer tes images).

👉 **Plan du Module Docker :**
Nous venons de voir l'Étage 1 (La philosophie).
S'il est validé par tes soins, nous passerons à l'**Étage 2** : "Le Chef d'Orchestre du Réseau & le stockage local SQLite" (Où tu montreras que tu maîtrises les Volumes et le Résolveur DNS Interne de Docker).
Puis l'**Étage 3** : "L'optimisation des Images", qui dévoilera ton Dockerfile en Multi-Stage (ton argument coup de poing !).
