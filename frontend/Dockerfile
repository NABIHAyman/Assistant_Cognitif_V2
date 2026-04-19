# ==============================================================================
# ÉTAPE 1 : LE BUILDER (L'Usine de construction)
# ==============================================================================
# On utilise Node LTS basé sur Alpine pour compiler le code Vue.js.
# On nomme cette étape "build-stage" pour pouvoir y faire référence plus tard.
FROM node:22-alpine AS build-stage

# On définit le dossier de travail dans le conteneur
WORKDIR /app

# OPTIMISATION DU CACHE DOCKER :
# On copie d'abord UNIQUEMENT les fichiers de dépendances.
# Si tu modifies ton code Vue.js sans toucher aux dépendances, Docker sautera le 'npm install' !
COPY package*.json ./
RUN npm install

# On copie le reste du code source de l'interface
COPY . .

# On lance la compilation (Vite va transformer Vue + Tailwind en HTML/JS pur)
RUN npm run build


# ==============================================================================
# ÉTAPE 2 : LA PRODUCTION (Le Serveur Ultra-Léger)
# ==============================================================================
# On jette toute l'usine Node.js et on repart d'une image Nginx Alpine (très légère et sécurisée)
FROM nginx:alpine AS production-stage

# On supprime la page d'accueil par défaut de Nginx
RUN rm -rf /usr/share/nginx/html/*

# LE "FLEX" MULTI-STAGE : On récupère UNIQUEMENT le dossier '/app/dist' généré
# par l'usine de l'Étape 1. Le reste (node_modules, code source) est détruit.
COPY --from=build-stage /app/dist /usr/share/nginx/html

# On copie notre configuration Nginx personnalisée (Indispensable pour Vue.js)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# On expose le port 80 (qui sera mappé sur le 3000 par ton docker-compose)
EXPOSE 80

# On lance Nginx en premier plan pour que le conteneur ne s'éteigne pas
CMD ["nginx", "-g", "daemon off;"]