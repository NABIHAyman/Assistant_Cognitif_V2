import os
import json
from loguru import logger

def get_knowledge_context(base_path: str) -> str:
    """
    Récupère la taxonomie et l'arborescence des fichiers existants.
    Fournit le chemin relatif exact pour sécuriser l'action 'append'.
    """
    logger.debug(f"🔍 Scan de la base de connaissances : {base_path}")

    meta_path = os.path.join(base_path, "_meta/domains.json")

    # 1. On récupère les thèmes autorisés (Taxonomie)
    taxonomy = "Aucune taxonomie définie."
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                taxonomy = f.read()
            logger.debug("✅ Taxonomie domains.json chargée.")
        except Exception as e:
            logger.error(f"❌ Erreur lecture domains.json : {e}")
    else:
        # Le warning doit être ici, dans le ELSE du IF EXISTS
        logger.warning(f"⚠️ Fichier manquant : {meta_path}")

    # 2. On construit l'arborescence visuelle avec les CHEMINS RELATIFS
    tree_str = ""
    file_count = 0
    for root, dirs, files in os.walk(base_path):
        # On ignore les dossiers techniques
        dirs[:] = [d for d in dirs if not d.startswith(('.', '_')) and d != 'proposals']

        level = root.replace(base_path, '').count(os.sep)
        indent = '  ' * level
        folder_name = os.path.basename(root)

        if folder_name and folder_name != os.path.basename(base_path):
            tree_str += f"{indent}- [Dossier] {folder_name}/\n"

        subindent = '  ' * (level + 1)
        for f in files:
            if f.endswith('.md'):
                file_count += 1
                # 🛡️ CORRECTION CRITIQUE : Calcul du chemin relatif
                # Ex: "tech/backend/aspnet.md" au lieu de juste "aspnet.md"
                rel_dir = os.path.relpath(root, base_path)
                rel_path = os.path.join(rel_dir, f).replace("\\", "/") if rel_dir != "." else f

                # On montre le chemin complet à l'IA pour qu'elle puisse le copier-coller dans 'target_file'
                tree_str += f"{subindent}- {rel_path}\n"

    if not tree_str.strip():
        tree_str = "Aucun fichier existant."
        logger.info("ℹ️ L'arborescence de la mémoire est vide.")
    else:
        logger.info(f"📊 Contexte généré : {file_count} fichiers Markdown détectés.")

    return f"""
--- TAXONOMIE (DOMAINES ET TAGS AUTORISÉS) ---
{taxonomy}

--- ARBORESCENCE ET FICHIERS CIBLES (Pour l'action 'append') ---
{tree_str}
"""