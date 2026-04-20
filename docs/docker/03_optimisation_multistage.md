# 🏗️ Étage 3 : L'Art Incompris du Multi-Stage Build

Bienvenue dans le dernier socle de présentation de ta sagacité Docker. Jusqu'ici, nous avons organisé la ville (Le Docker Compose). Il est temps de plonger dans le bâtiment proprement dit : le `Dockerfile` du Frontend.
C'est ici qu'une simple application peut passer d'un statut "amateur" de 1.5 Go, à une capsule professionnelle de 30 Mo. La magie s'appelle le **Multi-Stage Build**.

## 1. Le Piège de l'Écosystème Node.js
Pour construire ton frontend en Vue.js + Tailwind, tu as impérativement besoin de l'environnement **Node.js**. 
Ce monstre est lourd. Lorsque tu tapes `npm install` dans ton projet, il va télécharger `node_modules` (des milliers de milliers de micro-fichiers) : outils de compression CSS, transpileurs Babel, et serveurs Vite. 
En développement, c'est indispensable. En production, **c'est un boulet**.

Si tu mets tout ça dans l'image Docker finale (ce que font 90% des tutoriels sur internet avec le mot clé `CMD ["npm", "run", "dev"]`), ton conteneur prendra de la mémoire RAM inutile, s'allumera lentement, et sera un gruyère de failles de sécurité.

## 2. Étape 1 : Usiner (build-stage)
Regarde l'astuce fondamentale dans ton fichier `frontend/Dockerfile` :
```dockerfile
# USINE DE COMPILATION (LOURDE)
FROM node:22-alpine AS build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
```
Tu instancies ton usine massive (`node:22-alpine`), tu crées l'immense dossier `node_modules`, et tu lances la machine (`npm run build`). Vite et Tailwind transforment tout ton code complexe en fichiers Javascript et HTML ultra-légers et minifiés, disponibles dans un petit répertoire nommé `/dist`.
L'usine a terminé sa tâche.

## 3. Étape 2 : L'Épuration (production-stage)
La ligne suivante est là où le cerveau DevOps opère sa poésie :
```dockerfile
# SERVEUR EXTREMEMENT LEGER
FROM nginx:alpine AS production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
```
Instantanément, tu **renvoies l'usine Node à la casse**. Le premier `FROM node:22` et ses gigaoctets disparaissent dans le néant.
Tu redémarres avec une coquille vide hyper-légère (`nginx:alpine`).
Puis, tu ordonnes à Docker : `"Récupère EXCLUSIVEMENT le dossier /app/dist depuis les décombres de la build-stage, et mets-le ici !"`.

## 4. Les 3 Bénéfices Industriels Majeurs
Il faut absolument glisser ce triptyque lors de ta soutenance ou de ton module :
1. **La Taille** : Ton image Docker finale ne s'encombre d'aucun outil, elle passe de potentiellement 1500 Mo à moins de ~30 Mo.
2. **La Vitesse** : Avec un poids plume, ton image est "push" et s'exécute sur le réseau en quelques dizaines de secondes, idéal pour l'Autoscaling du futur.
3. **La Sécurité (Le facteur X)** : Imaginons qu'un hacker parvienne à faire une injection sur le navigateur de quelqu'un (`XSS`) pour attaquer ton serveur web. S'il réussit, il se retrouve face au conteneur final (celui du Nginx). Sauf qu'à l'intérieur : il n'y a pas Python. Il n'y a pas Bash complet. Il n'a même pas de compilateur Node.js ! **Il ne peut litéralement rien exécuter de malfaisant**. Tu as "bunkerisé" le site.

---

**💡 Pour ton module Docker :**
Ce 3e et dernier étage est un "Mic-Drop" académique. Le Multi-Stage build permet de casser complètement l'idée reçue selon laquelle *"Docker rend les applications lourdes"*. L'Isolation, le Résal Réseau et le Multi-Stage sont les trois piliers du Container Engineering moderne.

👉 **Mission accomplie !** L'histoire de la conteneurisation de ton application Cognitif est maintenant parfaitement formalisée pour briller dans les yeux de ton jury académique. 🚀
