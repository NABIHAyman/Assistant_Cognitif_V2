# 🧠 Prompt Engineering Déclaratif & Anti-Hallucinations

Niveau 2 de notre Cerveau IA. +30 % de technicité. On abandonne le blabla pour regarder ce qui fait marcher Pydantic-AI : **Le Typage Fort**.

## 1. Pourquoi Pydantic ? "Ceci n'est pas un texte"
L'IA (Ollama, ChatGPT, etc.) est probabiliste. Elle prédit le prochain mot. Pour elle, `{"titre": "toto"}` est juste un texte sympa.
Si tu avais écrit le code avec des prompts habituels ("Renvoie moi un JSON s'il te plait"), tôt ou tard tu aurais eu un système qui crashe en production par un `JSONDecodeError`.

Ton approche avec Pydantic est dite **Déclarative**. Observe ta classe issue de `main.py` :
```python
class ProposalResult(BaseModel):
    title: str = Field(description="Titre convention domaine_concept")
    action: str = Field(description="action: 'create', 'append' ou 'ignore'")
    is_new_domain: bool = Field(description="True si nouveau dossier")
    # ...
```

Ici, tu ne configures pas qu'une simple classe. Derrière le rideau, `pydantic_ai` prend cette classe pour **générer lui-même** un schéma formel compréhensible par l'IA (du type JSON Schema). L'IA reçoit donc un cadre mathématique qu'elle est contrainte de respecter.

## 2. Le Double-Blind System (La Ruse de GitDock)
Malgré le typage rigoureux, certains modèles tournant sur ton PC (`gemma4` ou autre) aiment ajouter des enrobages indésirables : 
> *"Voici votre réponse : ```json { ... } ``` Bonne journée !"*

Ton code utilise la "Ruse" du parseur `parse_ai_response()`. Voyons comment ce pansement de charpentier industriel fonctionne :

```python
def parse_ai_response(raw_text: str) -> ProposalResult:
    # 1. On arrache les "```json" et autres backticks qui sont du bruit
    raw_text = raw_text.replace('```json', '').replace('```', '').strip()
    
    # 2. Si ça ne commence pas par une accolade, on tronque tout ce qu'il y a avant
    if not raw_text.startswith('{'):
        raw_text = '{' + raw_text.split('{', 1)[1]
        
    # 3. Pareil pour la fin, on efface tout ce qui traîne après "}"
    if not raw_text.endswith('}'):
        raw_text = raw_text.rsplit('}', 1)[0] + '}'
        
    # 4. Enfin, on passe l'objet à Pydantic pour validation
    parsed_json = json.loads(raw_text)
    return ProposalResult.model_validate(parsed_json)
```
C'est le côté "Artisan-Hacker" du code ! Peu importe à quel point l'IA hallucine autour de ton objet métier, ta tronçonneuse Python découpera la viande pour ne garder que le noyau parfait avant de la soumettre au contrôle final `model_validate()`.

## 3. Le Système de Gabarit Intégré (Le Template)
Tu as aussi solidifié le contexte (`SYSTEM_PROMPT`) en attachant directement le `JSON_TEMPLATE`. 
Non seulement le modèle subit la contrainte `ProposalResult` générée par Pydantic, mais il reçoit aussi `JSON_TEMPLATE` écrit en dur avec un exemple final ("`Ceiling Effect`" en Machine Learning). Cela empêche l'IA de partir trop loin dans l'abstrait et recentre sa concentration sur la complétion par mimétisme.

---

**💡 Ce qu'il faut retenir de ce pallier :**
Tu as traité le LLM pour ce qu'il est : **une fonction imprévisible**. Et tu as traité ton Backend pour ce qu'il est : **une machine stricte**. Tu as créé le pont parfait entre la prédiction aléatoire et le typage industriel à l'aide de Pydantic et de Regex/String parsing.

**👉 Prochainement :** Nous irons voir comment injecter l'historique et la connaissance de ton système au modèle. C'est en faisant cela que l'IA devient "intelligente" et passe d'un vulgaire traducteur à un véritable architecte de données.
