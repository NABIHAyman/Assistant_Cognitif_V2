# backend/app/main.py
import os
import io
import glob
import shutil
import json
from PIL import Image
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, BackgroundTasks, Body, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.messages import BinaryContent
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIChatModel

# 🛡️ LE BOUCLIER ANTI-PROXY (Inspiré de GitDock)
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["NO_PROXY"] = "127.0.0.1,localhost,100.89.63.25,host.docker.internal,*"

# Imports internes
from app.models import Proposition, get_db, SessionLocal
from app.utils.tree_helper import get_knowledge_context
from app.executor import _write_markdown, _update_taxonomy, _call_mcp_notion
from app.config import app_settings


import logfire  # <--- AJOUTER
from loguru import logger  # <--- AJOUTER
import sys

app = FastAPI(title="Cognition Web API", version="2.0")


# 1. Configuration de Loguru (Console + Fichier qui ne sature pas le disque)
logger.remove() # Enlève le logger par défaut
logger.add(sys.stdout, colorize=True, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>")
logger.add("/app/data/logs/cognition_backend.log", rotation="10 MB", retention="10 days", level="DEBUG", backtrace=True, diagnose=True)
logger.info("🚀 Système Cognitif V2 démarré - Opération Mouchards active.")

# 2. Le Filet de Sécurité Global (Catch-All Exception Handler)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Attrape TOUT ce qui fait crasher FastAPI et l'écrit dans le log avec la stack trace."""
    logger.error(f"💥 CRASH FATAL NON GÉRÉ sur la route {request.url.path}")
    logger.exception(exc) # 👈 C'est ÇA qui logge "tout ce qui bouge" (traceback complet)
    return JSONResponse(
        status_code=500,
        content={"detail": "Le serveur a explosé en vol. Regarde /data/logs/cognition_backend.log"}
    )


class ProposalResult(BaseModel):
    title: str = Field(description="Titre convention domaine_concept")
    action: str = Field(description="action: 'create', 'append' ou 'ignore'")
    target_file: str | None = Field(default=None, description="Chemin cible pour append")
    domain: str = Field(description="Dossier thématique")
    is_new_domain: bool = Field(description="True si nouveau dossier suggéré")
    existing_tags_used: list[str] = Field(description="Tags existants piochés")
    proposed_new_tags: list[str] = Field(description="Nouveaux tags suggérés")
    markdown_content: str | None = Field(default=None, description="Contenu Markdown")
    reasoning: str = Field(description="Raisonnement de l'IA")


# ==============================================================================
# 🌟 LA RUSE : PARSING ET TEMPLATE (Inspiré de GitDock)
# ==============================================================================

def extract_text_from_result(result) -> str:
    """Extrait le texte de la réponse du LLM, peu importe la version de PydanticAI."""
    try:
        if hasattr(result, 'output') and isinstance(result.output, str):
            return result.output
        elif hasattr(result, 'data') and isinstance(result.data, str):
            return result.data
        elif hasattr(result, 'all_messages'):
            messages = result.all_messages()
            if messages:
                last_msg = messages[-1]
                if hasattr(last_msg, 'parts'):
                    for part in last_msg.parts:
                        if hasattr(part, 'content'):
                            return str(part.content)
                        elif hasattr(part, 'text'):
                            return str(part.text)
    except Exception as e:
        print(f"⚠️ Erreur d'extraction : {e}")
    return str(result)


def parse_ai_response(raw_text: str) -> ProposalResult:
    """Nettoie les balises markdown et valide avec Pydantic."""
    raw_text = raw_text.replace('```json', '').replace('```', '').strip()
    if not raw_text.startswith('{'):
        raw_text = '{' + raw_text.split('{', 1)[1]
    if not raw_text.endswith('}'):
        raw_text = raw_text.rsplit('}', 1)[0] + '}'
    parsed_json = json.loads(raw_text)
    return ProposalResult.model_validate(parsed_json)


JSON_TEMPLATE = """
\n\n--- INSTRUCTION DE FORMATAGE OBLIGATOIRE ---
Tu es un système automatisé. Tu dois générer EXCLUSIVEMENT un objet JSON valide.
Remplis ce template exact avec tes propres résultats :
{
  "title": "titre_du_sujet",
  "action": "create",
  "target_file": "dossier/fichier.md",
  "domain": "tech/backend",
  "is_new_domain": false,
  "existing_tags_used": ["#tag1"],
  "proposed_new_tags": ["#tag2"],
  "markdown_content": "# Titre\\n\\nContenu pédagogique ici...",
  "reasoning": "J'ai choisi cette action car..."
}
Ne rajoute AUCUN texte avant ou après ce JSON.
"""

with open("app/core/instructions.md", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read() + JSON_TEMPLATE

# ==============================================================================
# CONFIGURATION DE L'AGENT (SANS le result_type qui crashe)
# ==============================================================================
def get_agent():
    """Génère l'Agent IA dynamiquement en fonction des paramètres "à chaud"."""
    conf = app_settings.settings
    if conf.llm_provider == "gemini":
        return Agent('gemini-2.5-flash-lite', system_prompt=SYSTEM_PROMPT)
    else:
        provider = OpenAIProvider(base_url=f"{conf.ollama_host}/v1", api_key="ollama-local")
        return Agent(OpenAIChatModel(conf.ollama_model, provider=provider), system_prompt=SYSTEM_PROMPT)


# ==============================================================================
# ROUTES API
# ==============================================================================

@app.post("/api/analyze")
async def analyze_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    logger.info(f"📥 Réception d'une image individuelle : {file.filename}")

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Doit être une image.")

    image_bytes = await file.read()
    try:
        conf = app_settings.settings
        img = Image.open(io.BytesIO(image_bytes))
        img.thumbnail((conf.image_resolution, conf.image_resolution))
        img = img.convert("RGB")
        buffer = io.BytesIO()
        img.save(buffer, format="WEBP", quality=conf.image_quality)
        optimized_image = buffer.getvalue()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    base_path = "/app/data/knowledge-base"
    knowledge_context = get_knowledge_context(base_path)

    logger.debug(f"🧠 Appel de l'IA pour {file.filename}...")
    try:
        prompt_text = f"Voici l'état actuel de ma mémoire :\n{knowledge_context}\n\nAnalyse cette image."
        
        # --- MODE DRY_RUN ---
        is_dry_run = app_settings.settings.dry_run
        if is_dry_run:
            # Estimation (1 texte token ≈ 4 chars) + 1000 tokens fixes pour le poids de l'image (Gemini/Ollama)
            estimated_tokens = (len(SYSTEM_PROMPT) + len(prompt_text)) // 4 + 1000
            logger.warning(f"🛑 [DRY RUN ACTIF] Appel IA annulé pour {file.filename}.")
            logger.info("="*50)
            logger.info(f"🧠 PROMPT SYSTÈME :\n{SYSTEM_PROMPT}")
            logger.info("-" * 50)
            logger.info(f"👤 PROMPT UTILISATEUR :\n{prompt_text}")
            logger.info("="*50)
            logger.warning(f"💰 COÛT ESTIMÉ POUR CE CALL : ~{estimated_tokens} tokens.")
            return {
                "status": "ignored", 
                "reasoning": f"[DRY RUN] Coût estimé : {estimated_tokens} tokens. Le prompt exact a été affiché dans les logs du backend. L'appel IA n'a pas été exécuté."
            }
        
        agent = get_agent()
        result = await agent.run(
            [
                prompt_text,
                BinaryContent(data=optimized_image, media_type='image/webp')
            ],
            model_settings={'temperature': app_settings.settings.temperature}
        )

        # 🌟 UTILISATION DU PARSEUR DE GITDOCK
        raw_text = extract_text_from_result(result)
        try:
            ai_data = parse_ai_response(raw_text)
            logger.info(f"✅ Analyse réussie pour {file.filename}. Action : {ai_data.action}")
        except json.JSONDecodeError:
            logger.error(f"❌ Hallucination JSON de l'IA (JSONDecodeError). Texte brut :\n{raw_text}")
            raise HTTPException(
                status_code=503, 
                detail="Le Moteur IA a produit un format de réponse invalide (Hallucination JSON). Veuillez réessayer cette image."
            )

        if ai_data.action == "ignore":
            return {"status": "ignored", "reasoning": ai_data.reasoning, "message": "Bruit."}

        nouvelle_proposition = Proposition(
            title=ai_data.title, action=ai_data.action, target_file=ai_data.target_file,
            domain=ai_data.domain, is_new_domain=ai_data.is_new_domain,
            existing_tags=",".join(ai_data.existing_tags_used), proposed_new_tags=",".join(ai_data.proposed_new_tags),
            markdown_content=ai_data.markdown_content, reasoning=ai_data.reasoning, status="pending",
            source_image=file.filename
        )
        db.add(nouvelle_proposition)
        db.commit()
        db.refresh(nouvelle_proposition)
        return {"status": "success", "data": nouvelle_proposition}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def process_batch_background():
    logger.info("🔄 Démarrage d'un batch de traitement en arrière-plan...")

    inbox_path, archive_path, trash_path = "/app/data/inbox", "/app/data/archive", "/app/data/trash"
    os.makedirs(inbox_path, exist_ok=True)
    os.makedirs(archive_path, exist_ok=True)
    os.makedirs(trash_path, exist_ok=True)

    image_files = []
    for ext in ["*.jpg", "*.jpeg", "*.png", "*.webp"]:
        image_files.extend(glob.glob(os.path.join(inbox_path, ext)))
        image_files.extend(glob.glob(os.path.join(inbox_path, ext.upper())))

    if not image_files:
        logger.warning("Empty Inbox : Aucune image trouvée dans /data/inbox")
        return

    logger.info(f"📁 {len(image_files)} images détectées dans l'inbox.")

    db = SessionLocal()
    try:
        base_path = "/app/data/knowledge-base"
        knowledge_context = get_knowledge_context(base_path)
        for image_path in image_files:
            filename = os.path.basename(image_path)
            logger.debug(f"⚙️ Traitement de {filename}...")
            try:
                conf = app_settings.settings
                with open(image_path, "rb") as f:
                    image_bytes = f.read()
                img = Image.open(io.BytesIO(image_bytes))
                img.thumbnail((conf.image_resolution, conf.image_resolution))
                img = img.convert("RGB")
                buffer = io.BytesIO()
                img.save(buffer, format="WEBP", quality=conf.image_quality)
                optimized_image = buffer.getvalue()

                prompt_text = f"Voici l'état actuel de ma mémoire :\n{knowledge_context}\n\nAnalyse cette image."

                # --- MODE DRY_RUN ---
                is_dry_run = app_settings.settings.dry_run
                if is_dry_run:
                    estimated_tokens = (len(SYSTEM_PROMPT) + len(prompt_text)) // 4 + 1000
                    logger.warning(f"🛑 [DRY RUN ACTIF] {filename} bypassée.")
                    logger.info("="*50)
                    logger.info(f"👤 PROMPT UTILISATEUR ENVOYÉ NORMALEMENT : \n{prompt_text}")
                    logger.info("="*50)
                    logger.warning(f"💰 COÛT ESTIMÉ : ~{estimated_tokens} tokens. (Fichier conservé dans l'inbox).")
                    continue  # Ne déplace pas le fichier, passe au suivant.

                agent = get_agent()
                result = await agent.run(
                    [
                        prompt_text,
                        BinaryContent(data=optimized_image, media_type='image/webp')
                    ],
                    model_settings={'temperature': app_settings.settings.temperature}
                )

                # 🌟 UTILISATION DU PARSEUR DE GITDOCK
                raw_text = extract_text_from_result(result)
                try:
                    ai_data = parse_ai_response(raw_text)
                except json.JSONDecodeError:
                    logger.error(f"❌ Hallucination JSON sur le fichier {filename}. Parse impossible. Fichier laissé dans l'inbox pour le prochain retry.")
                    continue  # Laisse le fichier dans l'inbox et passe au suivant

                if ai_data.action == "ignore":
                    shutil.move(image_path, os.path.join(trash_path, os.path.basename(image_path)))
                    continue

                nouvelle_proposition = Proposition(
                    title=ai_data.title, action=ai_data.action, target_file=ai_data.target_file,
                    domain=ai_data.domain, is_new_domain=ai_data.is_new_domain,
                    existing_tags=",".join(ai_data.existing_tags_used),
                    proposed_new_tags=",".join(ai_data.proposed_new_tags),
                    markdown_content=ai_data.markdown_content, reasoning=ai_data.reasoning, status="pending",
                    source_image=os.path.basename(image_path)
                )
                db.add(nouvelle_proposition)
                db.commit()
                shutil.move(image_path, os.path.join(archive_path, os.path.basename(image_path)))
            except Exception as e:
                logger.error(f"❌ Erreur critique sur {image_path}")
                logger.exception(e)  # Logge toute la stack trace d'erreur
    finally:
        db.close()


@app.post("/api/upload/inbox")
async def upload_to_inbox(files: list[UploadFile] = File(...)):
    logger.info(f"📥 Réception d'un upload batch : {len(files)} fichiers.")
    inbox_path = "/app/data/inbox"
    os.makedirs(inbox_path, exist_ok=True)
    
    uploaded_files = []
    for file in files:
        if file.content_type.startswith("image/"):
            # Sécurité de base sur le nom
            safe_filename = os.path.basename(file.filename)
            file_path = os.path.join(inbox_path, safe_filename)
            try:
                # Écriture directe sur le disque
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                uploaded_files.append(safe_filename)
                logger.debug(f"✅ Fichier sauvegardé dans l'inbox : {safe_filename}")
            except Exception as e:
                logger.error(f"❌ Erreur sauvegarde {safe_filename}: {str(e)}")
        else:
            logger.warning(f"⚠️ Fichier ignoré (non-image) : {file.filename}")

    return {
        "status": "success", 
        "message": f"{len(uploaded_files)} images téléchargées dans l'inbox pour le traitement par lots.",
        "files": uploaded_files
    }

@app.post("/api/analyze/batch")
async def trigger_batch_analysis(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_batch_background)
    return {"status": "success", "message": "Batch lancé en arrière-plan."}


@app.get("/api/proposals")
def get_pending_proposals(db: Session = Depends(get_db)):
    proposals = db.query(Proposition).filter(Proposition.status == "pending").all()
    return {
        "proposals": [
            {
                "id": p.id, "title": p.title, "action": p.action,
                "target_file": p.target_file, "domain": p.domain,
                "is_new_domain": p.is_new_domain, "existing_tags": p.existing_tags,
                "proposed_new_tags": p.proposed_new_tags,
                "markdown_content": p.markdown_content, "reasoning": p.reasoning,
                "source_image": p.source_image, "status": p.status
            }
            for p in proposals
        ]
    }


@app.post("/api/publish/{prop_id}")
async def publish_proposal(prop_id: int, payload: dict = Body({}), db: Session = Depends(get_db)):
    proposition = db.query(Proposition).filter(Proposition.id == prop_id).first()
    if not proposition or proposition.status != "pending":
        raise HTTPException(status_code=404, detail="Non traitable.")

    if payload:
        proposition.title = payload.get("title", proposition.title)
        proposition.domain = payload.get("domain", proposition.domain)
        proposition.action = payload.get("action", proposition.action)
        proposition.target_file = payload.get("target_file", proposition.target_file)
        proposition.markdown_content = payload.get("markdown_content", proposition.markdown_content)
        proposition.existing_tags = payload.get("tags", proposition.existing_tags)

    logger.info(f"📤 Publication demandée pour la proposition ID {prop_id} : {proposition.title}")

    base_path = "/app/data/knowledge-base"
    file_path = _write_markdown(base_path, proposition)
    _update_taxonomy(base_path, proposition)
    notion_result = await _call_mcp_notion(proposition)

    proposition.status = "approved"
    db.commit()
    return {"status": "success", "message": "Approuvé.", "notion": notion_result}


@app.post("/api/reject/{prop_id}")
def reject_proposal(prop_id: int, db: Session = Depends(get_db)):
    proposition = db.query(Proposition).filter(Proposition.id == prop_id).first()
    if proposition:
        proposition.status = "rejected"
        db.commit()
    return {"status": "rejected"}


@app.get("/api/settings")
def get_settings():
    return app_settings.get_all()

@app.post("/api/settings")
def update_settings(payload: dict = Body(...)):
    app_settings.update(payload)
    return {"status": "success", "settings": app_settings.get_all()}


@app.get("/health")
def health_check():
    return {"status": "ok"}