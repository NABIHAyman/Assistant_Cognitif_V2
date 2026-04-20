# 🌐 Étage 2 : Le Chef d'Orchestre du Réseau & La Persistance Absolue

Pour ce deuxième niveau de présentation DevOps, nous allons détruire la plus grande incompréhension des débutants en Docker : **la virtualisation des réseaux et du stockage**.

## 1. La Cité Emancipée : Le Réseau `cognitif_net`
Les conteneurs sont conçus pour être paranoïaques : par défaut, un serveur web dans un conteneur et une base de données dans un autre ne peuvent pas s'entendre, même s'ils tournent sur le même PC.

Ici, tu as programmé la création d'un pont privé (Bridge) :
```yaml
networks:
  cognitif_net:
    driver: bridge
```
*   **Le Miracle du DNS Interne :** Si tu observes le fichier `frontend/nginx.conf` de ton projet, tu as écrit la règle : `proxy_pass http://backend:8000;`. 
Pourquoi pas une adresse IP (`192.168.x.x`) ? Parce que `docker-compose` possède son propre service DNS dynamique ! Tu n'as pas à te soucier des IPs. Nginx dit *"Je veux parler à backend"*, et Docker redirige magiquement la requête vers le bon conteneur dans `cognitif_net`. Trivial mais extrêmement puissant.

## 2. Le Pont-levis : `host.docker.internal`
Ta situation était très complexe : tu avais 3 services dockérisés (fermés dans `cognitif_net`) MAIS ton puissant moteur IA (Ollama) tournait *nativement sur Windows*. 

Pour percer le bunker de ton réseau privé Docker et redescendre sur ton ordinateur personnel, tu as utilisé l'astuce ultime des développeurs hybrides :
```yaml
environment:
  - OLLAMA_HOST=http://host.docker.internal:11434
extra_hosts:
  - "host.docker.internal:host-gateway" # Rend le VPN compatible sous Linux/Windows
```
Grâce à ce paramètre, le réseau Docker trouve l'IP physique exacte du PC "hôte" (le tien) sans que tu n'aies jamais à l'écrire en dur. Ton FastAPI discute ainsi avec ta carte graphique !

## 3. L'Éphémère vs L'Éternel (Les "Bind Mounts")
Il y a une règle d'or dans le Cloud : **L'intérieur d'un conteneur est éphémère.** Si tu éteins Docket (`docker-compose down`), absolument TOUT ce qui s'est passé dans un conteneur est désintégré (Base de données incluse). 

Ce serait catastrophique pour ton projet `Cognitif`, car chaque ligne du `SQLite` doit être conservée pour demain.
La solution élégante s'appelle le **Volume : Bind Mount** :
```yaml
# Backend Service
volumes:
  - ./data:/app/data
```
Tu as ordonné à Docker de percer un trou spatiotemporel. Le système lie physiquement `C:\...\Desktop\assistant_v2\data` de *ta* machine Windows, en le montant sur le répertoire virtuel `/app/data` de *Linux*. 
*   Quand SQLite modifie la donnée virtuelle, il sauvegarde *en fait* sur ton SSD réel. 
*   Quand FastAPI redémarre, il retrouve toute ta base de données intacte.

---

**💡 Pour ton module Docker :**
Ce 2ème étage montre que tu maîtrises un des piliers du DevOps : **l'isolation des états (Stateless vs Stateful)**. 
- *Le code (Stateless)* est détruit à la fermeture, car il est "gratuit" à reconstruire. 
- *La Data (Stateful)* est ancrée physiquement via un Volume pour assurer sa sauvegarde hors du cycle de vie volatile de Docker.
- Et les communications se font sans hard-coding (IPs en dur), utilisant le DNS interne du `bridge`.

👉 S'il te reste de l'énergie, donne le feu vert pour **l'Étage 3 final**. C'est là que l'on verra le "Multi-Stage Build" de ton frontend, la technique qui bluffera à coup sûr tes formateurs !
