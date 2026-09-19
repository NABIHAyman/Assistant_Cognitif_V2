# 🎯 Tâches Prioritaires Restantes (Roadmap V3)

Suite à l'analyse complète de l'architecture et des documents de conception actuels du projet Cognitif V2, voici l'état des lieux des développements futurs.

---

## 🔝 Top 3 des tâches les plus importantes à réaliser

Ces tâches découlent directement des documents de vision prospective (les chapitres "05_...") présents dans votre documentation. Elles visent à transformer Cognitif V2 en une application SaaS de niveau professionnel (V3).

### 1. 🔐 Système Multi-Utilisateurs & Authentification JWT
*Document de référence :* `01_parcours_fonctionnel/05_vision_multi_utilisateur_et_auth.md`
- **L'Enjeu :** Actuellement, le système ne possède pas de notion de "Propriété" (les propositions d'IA sont partagées pour toute personne ayant accès à l'API).
- **L'Action :** Mettre en place la sécurité et l'isolation des données avec l'implémentation de JSON Web Tokens (JWT). Ajouter un `user_id` aux tables de la base de données.
- **La Conséquence :** L'interface Vue.js passera d'un panneau d'administration global à un espace personnel sécurisé pour chaque utilisateur.

### 2. 🧠 RAG Vectoriel et Architecture Agents (Swarm)
*Document de référence :* `02_cerveau_ia/05_evolution_agents_multiples_et_rag_vectoriel.md`
- **L'Enjeu :** Sécuriser la scalabilité du système d'IA. Autant la lecture d'une arborescence de fichiers passe bien pour un petit projet `tree_helper`, mais elle atteindra les limites de tokens avec 40 000 notes.
- **L'Action :** 
  - Déployer une base de données vectorielle (ChromaDB ou PostgreSQL+pgvector) et faire du Retrieval-Augmented Generation (RAG) sémantique au lieu du texte brut.
  - Découper l'Agent IA unique en un "routeur d'agents" où plusieurs agents spécialisés (comptable, tech, etc.) analysent l'image selon son domaine en utilisant Pydantic-AI Agent Delegation.

### 3. 🐘 Migration PostgreSQL & Event Sourcing
*Document de référence :* `03_architecte_donnees/05_migration_vers_postgresql_et_event_sourcing.md`
- **L'Enjeu :** Abandonner SQLite pour la mise en production concurrentielle. 
- **L'Action :** Transitionner l'ORM SQLAlchemy vers PostgreSQL. Mettre en place les principes de l'Event Sourcing (enregistrer précisément chaque fois qu'une personne clique sur approuver, rejeter, ou modifier le titre).
- **La Conséquence :** Préparer le système pour de gros volumes transactionnels en évitant les verrous d'accès.

---

### 📘 Tâche Bonus (Niveau DevOps) : CI/CD et Déploiement Cloud Automatisé
- **L'Action :** Industrialiser le déploiement. Sortir de `docker-compose` simple pour aller vers du Kubernetes ou des services managés Cloud (AWS/GCP), automatisé par des pipelines (Github Actions / Gitlab CI).
