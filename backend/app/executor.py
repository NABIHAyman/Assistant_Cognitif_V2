# backend/app/executor.py
import os
import re
import json
from datetime import datetime
from app.models import Proposition
from fastmcp import Client  # Le client MCP natif 2026 !


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '_', text)
    return text


def _write_markdown(base_path: str, proposition: Proposition) -> str:
    if proposition.action == "append" and proposition.target_file:
        file_path = os.path.join(base_path, proposition.target_file)
    else:
        domain_dir = os.path.join(base_path, proposition.domain)
        os.makedirs(domain_dir, exist_ok=True)
        filename = f"{slugify(proposition.title)}.md"
        file_path = os.path.join(domain_dir, filename)

    all_tags = []
    if proposition.existing_tags:
        all_tags += proposition.existing_tags.split(",")
    if proposition.proposed_new_tags:
        all_tags += proposition.proposed_new_tags.split(",")

    tags_str = " ".join(t.strip() for t in all_tags if t.strip())
    date_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    header = (
        f"\n\n---\n"
        f"### 📅 Intégré le {date_str}\n"
        f"*Tags : {tags_str}*\n"
        f"**Justification :** {proposition.reasoning}\n\n"
    )

    content_block = header + (proposition.markdown_content or "")

    if proposition.action == "append" and os.path.exists(file_path):
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(content_block)
    else:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# {proposition.title}\n")
            f.write(content_block)

    return os.path.relpath(file_path, base_path)


def _update_taxonomy(base_path: str, proposition: Proposition):
    if not proposition.is_new_domain and not proposition.proposed_new_tags:
        return

    meta_path = os.path.join(base_path, "_meta/domains.json")
    os.makedirs(os.path.dirname(meta_path), exist_ok=True)

    taxonomy = {"version": "1.0", "domains": {}}
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            taxonomy = json.load(f)

    domains = taxonomy.setdefault("domains", {})

    if proposition.is_new_domain and proposition.domain not in domains:
        domains[proposition.domain] = {"description": "Auto-généré par l'IA", "keywords": [], "file_count": 0}

    if proposition.proposed_new_tags and proposition.domain in domains:
        existing = set(domains[proposition.domain].get("keywords", []))
        new_tags = [t.strip() for t in proposition.proposed_new_tags.split(",") if t.strip()]
        domains[proposition.domain]["keywords"] = list(existing | set(new_tags))

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(taxonomy, f, ensure_ascii=False, indent=2)


async def _call_mcp_notion(proposition: Proposition) -> dict:
    """Appelle le serveur MCP Notion via le Client MCP officiel."""
    all_tags = []
    if proposition.existing_tags:
        all_tags += [t.strip() for t in proposition.existing_tags.split(",")]
    if proposition.proposed_new_tags:
        all_tags += [t.strip() for t in proposition.proposed_new_tags.split(",")]

    try:
        # Connexion au serveur MCP distant via SSE (Server-Sent Events)
        async with Client("http://cognitif_mcp:8000/sse") as client:
            result = await client.call_tool(
                name="upsert_notion_page",
                arguments={
                    "metadata": {
                        "title": proposition.title,
                        "tags": [t for t in all_tags if t],
                        "markdown_content": proposition.markdown_content or ""
                    }
                }
            )
            return {"notion_status": "success", "detail": str(result)}

    except Exception as e:
        return {"notion_status": "warning", "detail": f"MCP injoignable: {str(e)}"}