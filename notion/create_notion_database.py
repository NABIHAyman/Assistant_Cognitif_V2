"""
Crée la base Notion « Cognition Memory » attendue par le connecteur MCP.

La structure (propriétés, options, vues) est lue dans cognition_memory.schema.json,
la même que celle décrite par le prompt Notion AI (notion-ai-prompt.md).

Prérequis :
  - une intégration interne Notion (NOTION_API_KEY) ;
  - une page Notion partagée avec cette intégration, qui accueillera la base
    (son ID, les 32 caractères de son URL : NOTION_PARENT_PAGE_ID).

Usage :
  pip install "notion-client>=3.1.0"
  python notion/create_notion_database.py --parent <ID_PAGE> [--write-env]

NOTION_API_KEY et NOTION_PARENT_PAGE_ID peuvent aussi venir de l'environnement
ou de mcp-server/.env, le fichier de secrets réservé au connecteur MCP.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

from notion_client import Client
from notion_client.errors import APIResponseError

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_FILE = Path(__file__).resolve().parent / "cognition_memory.schema.json"
ENV_FILE = ROOT / "mcp-server" / ".env"  # secrets Notion, isolés du backend

# Version de l'API Notion qui expose les data sources et la création de vues
NOTION_VERSION = "2026-03-11"


def read_env_file(path: Path) -> dict:
    """Lecture minimale d'un fichier .env (CLE=valeur, commentaires ignorés)."""
    values = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def setting(name: str, cli_value: str | None, env_file: dict) -> str | None:
    return cli_value or os.getenv(name) or env_file.get(name) or None


def notion_id(value: str) -> str:
    """Accepte un ID brut ou une URL Notion et renvoie l'ID (32 caractères hexadécimaux)."""
    # L'ID est à la fin du dernier segment de l'URL (« Titre-de-la-page-<id> »)
    candidate = value.split("?")[0].split("#")[0].rstrip("/").split("/")[-1].replace("-", "")[-32:]
    if not re.fullmatch(r"[0-9a-fA-F]{32}", candidate):
        sys.exit(f"ID Notion invalide : {value}")
    return candidate.lower()


def property_schema(spec: dict) -> dict:
    kind = spec["type"]
    if kind == "title":
        return {"type": "title", "title": {}}
    if kind in ("select", "multi_select"):
        return {"type": kind, kind: {"options": [{"name": name} for name in spec.get("options", [])]}}
    return {"type": kind, kind: {}}


def view_configuration(view: dict, property_ids: dict) -> dict:
    configuration = {
        "type": view["type"],
        "properties": [{"property_id": property_ids[name], "visible": True} for name in view["properties"]],
    }
    if view["type"] == "gallery":
        configuration["cover"] = {"type": view.get("cover", "page_content")}
        configuration["cover_size"] = view.get("cover_size", "medium")
    return configuration


def create_views(notion: Client, database_id: str, data_source_id: str, views: list, property_ids: dict) -> list:
    """Crée les vues du schéma ; la vue table par défaut de Notion est renommée plutôt que dupliquée."""
    warnings = []
    try:
        existing = notion.views.list(database_id=database_id).get("results", [])
    except APIResponseError:
        existing = []

    for view in views:
        configuration = view_configuration(view, property_ids)
        try:
            reusable = next((v for v in existing if v.get("type") == view["type"]), None)
            if reusable:
                notion.views.update(view_id=reusable["id"], name=view["name"], configuration=configuration)
                existing.remove(reusable)
            else:
                notion.views.create(database_id=database_id, data_source_id=data_source_id,
                                    name=view["name"], type=view["type"], configuration=configuration)
            print(f"  vue « {view['name']} » ({view['type']}) : OK")
        except APIResponseError as e:
            warnings.append(f"vue « {view['name']} » non créée ({e.code}) : à ajouter à la main dans Notion")
    return warnings


def write_env(database_id: str) -> None:
    lines = ENV_FILE.read_text(encoding="utf-8").splitlines() if ENV_FILE.exists() else []
    lines = [line for line in lines if not line.startswith("NOTION_DATABASE_ID=")]
    lines.append(f"NOTION_DATABASE_ID={database_id}")
    ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"NOTION_DATABASE_ID écrit dans {ENV_FILE}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Crée la base Notion « Cognition Memory ».")
    parser.add_argument("--parent", help="ID ou URL de la page Notion qui accueillera la base")
    parser.add_argument("--api-key", help="clé de l'intégration Notion (sinon NOTION_API_KEY)")
    parser.add_argument("--write-env", action="store_true", help="écrit NOTION_DATABASE_ID dans mcp-server/.env")
    args = parser.parse_args()

    env_file = read_env_file(ENV_FILE)
    api_key = setting("NOTION_API_KEY", args.api_key, env_file)
    parent = setting("NOTION_PARENT_PAGE_ID", args.parent, env_file)
    if not api_key or not parent:
        sys.exit("NOTION_API_KEY et la page parente (--parent ou NOTION_PARENT_PAGE_ID) sont requis.")

    schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    notion = Client(auth=api_key, notion_version=NOTION_VERSION)

    try:
        database = notion.databases.create(
            parent={"type": "page_id", "page_id": notion_id(parent)},
            title=[{"type": "text", "text": {"content": schema["database_name"]}}],
            icon={"type": "emoji", "emoji": schema["icon"]},
            is_inline=False,
            initial_data_source={
                "properties": {name: property_schema(spec) for name, spec in schema["properties"].items()}
            },
        )
    except APIResponseError as e:
        hint = " — la page parente est-elle partagée avec l'intégration ?" if e.code == "object_not_found" else ""
        sys.exit(f"Création refusée par Notion ({e.code}) : {e}{hint}")

    database_id = database["id"].replace("-", "")
    data_source_id = database["data_sources"][0]["id"]
    print(f"Base « {schema['database_name']} » créée : {database.get('url', database_id)}")

    properties = notion.data_sources.retrieve(data_source_id=data_source_id)["properties"]
    property_ids = {name: prop["id"] for name, prop in properties.items()}
    warnings = create_views(notion, database["id"], data_source_id, schema["views"], property_ids)

    for warning in warnings:
        print(f"  ⚠️  {warning}")
    print(f"\nNOTION_DATABASE_ID={database_id}")
    if args.write_env:
        write_env(database_id)


if __name__ == "__main__":
    main()
