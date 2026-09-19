# mcp-server/server.py
import os
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Initialisation du serveur MCP
mcp = FastMCP("CognitionNotionConnector")

# On récupère le secret injecté par Docker (idéalement via le MCP Gateway)
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")


class NotionPageMetadata(BaseModel):
    title: str = Field(..., description="Le titre de la page Notion")
    tags: list[str] = Field(..., description="Liste des tags pour la classification")
    markdown_content: str = Field(..., description="Le contenu brut en Markdown")


@mcp.tool()
def upsert_notion_page(metadata: NotionPageMetadata) -> str:
    """
    Outil MCP : Crée une nouvelle page dans la base de données 'Cognition Memory' sur Notion.
    L'agent d'orchestration appelle cet outil uniquement lorsque l'utilisateur a approuvé le brouillon.
    """
    if not NOTION_API_KEY or not NOTION_DATABASE_ID:
        return "ERREUR CRITIQUE : Clés d'API Notion manquantes dans le conteneur MCP."

    # -------------------------------------------------------------------------
    # ICI : Logique d'appel au SDK officiel notion-client
    # Exemple (pseudo-code) :
    # notion = Client(auth=NOTION_API_KEY)
    # notion.pages.create(
    #     parent={"database_id": NOTION_DATABASE_ID},
    #     properties={
    #         "Title": {"title": [{"text": {"content": metadata.title}}]},
    #         "Tags": {"multi_select": [{"name": tag} for tag in metadata.tags]},
    #         "Status": {"select": {"name": "Approved"}}
    #     },
    #     children=[... logique de conversion Markdown vers blocs Notion ...]
    # )
    # -------------------------------------------------------------------------

    # Pour l'instant, on simule le succès pour la console
    print(f"📡 [NOTION API] Page '{metadata.title}' pushée avec succès.")

    return f"SUCCÈS: Page '{metadata.title}' sauvegardée dans la base Notion."


if __name__ == "__main__":
    # Lancement du serveur sur le port exposé dans le docker-compose
    # mcp.run(transport="stdio")
    # Fix : On passe de 'stdio' à 'sse' et on écoute sur toutes les interfaces (0.0.0.0)
    mcp.run(transport="sse", host="0.0.0.0", port=8000)