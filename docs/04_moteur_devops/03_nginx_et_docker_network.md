# 🕵️ Le Reverse Proxy et le Bypass de Réseau

60 % de technicité DevOps. Ici, tout se joue sur un concept industriel que l'immense majorité des indépendants ignore : **Le Reverse Proxy Inversé Nginx**.

## 1. La Disparition du Démon CORS
Si tu as déjà fait du Web dev, tu connais la plaie de l'erreur rouge `CORS : Cross-Origin Resource Sharing bloqué`. Ça arrive quand `Vue.js` (tournant sur le port 3333) tente de faire un "fetch" à `FastAPI` (qui tourne sur le port 8020). Le navigateur s'y oppose fermement pour raisons de sécurité.

Beaucoup perdent des heures à coder des `middleware` compliqués dans FastAPI pour forcer l'acceptation.
**Tu l'as réglé dans le conteneur Nginx avec 4 lignes magistrales :**

```nginx
# frontend/nginx.conf
location /api/ {
    proxy_pass http://backend:8000/api;
}
```

Comment ça marche ?
1. Le navigateur n'appelle *jamais* le port du Backend. 
2. Vue.js demande juste à son propre Nginx local : `/api/proposals`.
3. Le navigateur bloque rien, car l'appel est local (same-origin).
4. Derrière le rideau (dans le conteneur `cognitif_net`), Nginx va chercher la réponse chez FastAPI (à l'adresse `backend:8000`) et la rend à Vue.js. C'est l'essence même du **Reverse Proxy**. Adieu le CORS.

## 2. Nginx vs Serveur de Développement
Il est important de comprendre une différence structurelle :
Quand tu déchiffiches Vue.js en local, tu fais un `npm run dev`. Vite (le bundle) démarre un serveur dynamique NodeJS pour te fournir la page.
Mais dans ce conteneur Docker de Production :
- Il y a eu un `npm run build` (voir Dockerfile du frontend).
- À la fin, Vue.js n'est plus du code intelligent. Ce n'est plus que des fichiers `.js` et `.html` inertes.
- C'est Nginx Alpine qui va lire ces fichiers statiques extraordinairement vite, et s'occuper de `try_files` (pour laisser Vue router ses propres pages SPA).

## 3. Le Lien Magique : Host.Docker.Internal
Rappelons le composant le plus étrange mais essentiel de cette infrastructure : Ollama local.
```yaml
environment:
  - OLLAMA_HOST=http://host.docker.internal:11434
extra_hosts:
  - "host.docker.internal:host-gateway"
```

Sans ce `extra_hosts` dans le `docker-compose.yml`, le conteneur backend est dans un bunker réseau (le fameux `cognitif_net`). 
Le mot clé `host-gateway` injecte de force l'IP de *ton ordinateur Windows de développement* (le `dell-info`) dans la carte réseau virtuelle du conteneur Linux. 

---
**💡 Résumé Pédagogique :**
L'architecture Docker/Nginx que tu as posée est propre : d'un côté, Nginx simule que ton application Backend est un composant de ton application Frontend (pour ne faire qu'UN seul service perçu par le navigateur), et de l'autre, Docker Compose ouvre un petit tunnel perçant le bunker (`host-gateway`) afin que FastAPI descende réclamer de la force de calcul LLM directement à l'Ollama natif au Windows. Tout communique. Magique.
