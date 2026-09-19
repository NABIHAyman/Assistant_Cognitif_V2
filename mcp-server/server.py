# mcp-server/server.py
import os
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from notion_client import Client
from notion_client.errors import APIResponseError
from pydantic import BaseModel, Field

# Initialisation du serveur MCP
mcp = FastMCP("CognitionNotionConnector")

# On récupère le secret injecté par Docker (idéalement via le MCP Gateway)
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Version de l'API Notion : 2026-03-11 accepte le contenu en Markdown à la création de page
NOTION_VERSION = os.getenv("NOTION_VERSION", "2026-03-11")

# Propriétés optionnelles de la base (utilisées seulement si elles existent avec le bon type)
TAGS_PROPERTY = os.getenv("NOTION_TAGS_PROPERTY", "Tags")
STATUS_PROPERTY = os.getenv("NOTION_STATUS_PROPERTY", "Status")
STATUS_VALUE = os.getenv("NOTION_STATUS_VALUE", "Approved")

# Limites de l'API Notion
TITLE_MAX_LENGTH = 2000
OPTION_MAX_LENGTH = 100

# Data source de la base et type de chaque propriété, résolus au premier appel
_target: dict | None = None


class NotionPageMetadata(BaseModel):
    title: str = Field(..., description="Le titre de la page Notion")
    tags: list[str] = Field(..., description="Liste des tags pour la classification")
    markdown_content: str = Field(..., description="Le contenu brut en Markdown")


def _notion() -> Client:
    return Client(auth=NOTION_API_KEY, notion_version=NOTION_VERSION)


def _resolve_target(notion: Client) -> dict:
    """Trouve le data source de la base et le type de ses propriétés (mis en cache)."""
    global _target
    if _target is None:
        database = notion.databases.retrieve(database_id=NOTION_DATABASE_ID)
        sources = database.get("data_sources") or []
        if not sources:
            raise ToolError("La base Notion n'expose aucun data source : est-elle partagée avec l'intégration ?")
        data_source_id = sources[0]["id"]
        schema = notion.data_sources.retrieve(data_source_id=data_source_id)["properties"]
        _target = {
            "data_source_id": data_source_id,
            "properties": {name: prop["type"] for name, prop in schema.items()},
        }
    return _target


def _clean_tag(tag: str) -> str:
    # Notion refuse les virgules dans les options multi_select
    return tag.strip().lstrip("#").replace(",", " ").strip()[:OPTION_MAX_LENGTH]


def _build_properties(metadata: NotionPageMetadata, property_types: dict) -> dict:
    """Construit les propriétés à partir du schéma réel de la base."""
    title_property = next(name for name, kind in property_types.items() if kind == "title")
    properties = {
        title_property: {"title": [{"type": "text", "text": {"content": metadata.title[:TITLE_MAX_LENGTH]}}]}
    }

    tags = [tag for tag in dict.fromkeys(_clean_tag(t) for t in metadata.tags) if tag]
    if tags and property_types.get(TAGS_PROPERTY) == "multi_select":
        properties[TAGS_PROPERTY] = {"multi_select": [{"name": tag} for tag in tags]}

    status_type = property_types.get(STATUS_PROPERTY)
    if status_type in ("select", "status"):
        properties[STATUS_PROPERTY] = {status_type: {"name": STATUS_VALUE}}

    return properties


@mcp.tool()
def upsert_notion_page(metadata: NotionPageMetadata) -> str:
    """
    Outil MCP : Crée une nouvelle page dans la base de données 'Cognition Memory' sur Notion.
    L'agent d'orchestration appelle cet outil uniquement lorsque l'utilisateur a approuvé le brouillon.
    """
    if not NOTION_API_KEY or not NOTION_DATABASE_ID:
        raise ToolError("ERREUR CRITIQUE : Clés d'API Notion manquantes dans le conteneur MCP.")

    notion = _notion()
    try:
        target = _resolve_target(notion)
        page_content = {"markdown": metadata.markdown_content} if metadata.markdown_content.strip() else {}
        page = notion.pages.create(
            parent={"type": "data_source_id", "data_source_id": target["data_source_id"]},
            properties=_build_properties(metadata, target["properties"]),
            **page_content,
        )
    except APIResponseError as e:
        raise ToolError(f"Notion a refusé la création de la page ({e.code}) : {e}") from e

    print(f"📡 [NOTION API] Page '{metadata.title}' créée : {page.get('url', page['id'])}")
    return f"SUCCÈS: Page '{metadata.title}' sauvegardée dans la base Notion ({page.get('url', page['id'])})."


if __name__ == "__main__":
    # Lancement du serveur sur le port exposé dans le docker-compose
    # mcp.run(transport="stdio")
    # Fix : On passe de 'stdio' à 'sse' et on écoute sur toutes les interfaces (0.0.0.0)
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
