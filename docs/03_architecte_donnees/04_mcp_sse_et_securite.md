# 🌉 SSE & Le Principe de Moindre Privilège : L'Outil MCP

Atteignons les 100% de technicité sur les données ! Pourquoi donc le Model Context Protocol est-il un conteneur physique (`mcp-server`) à part entière, et non pas simplement un bout de code branché directement dans FastAPI ? 

## 1. La Transmission SSE (Server-Sent Events)
Regarde au bas de l'application serveur (`server.py`) :
```python
mcp.run(transport="sse", host="0.0.0.0", port=8000)
```
Si tu avais utilisé le protocole classique "stdio", ton script MCP exigerait d'être exécuté dans le même "ordinateur" (le même terminal physique) que FastAPI. 
En choisissant **"sse"**, tu as transformé ton Serveur MCP en un véritable Service Web (un microservice !). FastAPI peut ainsi s'y connecter via :
```python
# Côté FastAPI backend
async with Client("http://cognitif_mcp:8000/sse") as client:
```
Le "SSE" (Event source) maintient une connexion ouverte entre FastAPI et ton MCP. Par rapport au REST classique (qui ouvre et ferme sans cesse la porte), SSE garde le tuyau ouvert. La communication est asynchrone et instantanée.

## 2. Le Principe de Moindre Privilège (Cyber-Sécurité)
Tu as protégé ton architecture via une notion cruciale : la sécurité des clés.
```python
# Côté MCP
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
```
Ces clés secrètes qui donnent accès à tout ton écosystème ne sont **pas** présentes dans le conteneur Backend !
Si un hacker ou un script malicieux réussit un jour à forcer FastAPI (parce qu'un port 8020 est ouvert sur le net), il n'aura accès qu'à ton image `WEBP` et la `sqlite` temporaire. **Jamais** il ne trouvera ta clé Notion là-bas.

Ton conteneur MCP (l'architecte des données finales) reste dissimulé au fond de ton Docker Compose. Il ne parle à personne d'autre qu'au backend, car tu as masqué ses ports publics (sauf pour le dev local). 

## 3. La Promesse MCP
En annotant la fonction Notion avec `@mcp.tool()`, tu crées ce qu'on appelle une interface standardisée.
Demain, si tu souhaites faire fonctionner ce même transfert Notion depuis un autre client MCP (un IDE, un assistant de bureau ou un tout autre agent, plutôt que ton projet Cognitif), ce conteneur `mcp-server` n'a pas besoin de la moindre modification. Il est auto-descriptif et respecte le standard MCP (Model Context Protocol).

---
**💡 Le Bilan d'Expert :**
Tu n'as pas codé un "script Python qui push vers Notion". Tu as construit un **Microservice Isolée et Agnostique**. Il respecte les règles de cyber-sécurité moderne via l'isolation des clés (Zero-Trust interne) tout en offrant une interface temps réel ultra performante via le protocole SSE.
