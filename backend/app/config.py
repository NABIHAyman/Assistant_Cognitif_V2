import os
import json
from loguru import logger
from pydantic import BaseModel

CONFIG_FILE = "/app/data/settings.json"

class AppConfigModel(BaseModel):
    # Cerveau IA
    llm_provider: str = os.getenv("LLM_PROVIDER", "ollama")
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "gemma4:e4b")
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))
    
    # DevOps (Moteur)
    dry_run: bool = os.getenv("DRY_RUN", "false").lower() in ["true", "1", "yes"]
    
    # Traitement Visuel (Rétine)
    image_resolution: int = int(os.getenv("IMAGE_RESOLUTION", "768"))
    image_quality: int = int(os.getenv("IMAGE_QUALITY", "65"))

class ConfigManager:
    def __init__(self):
        self.settings = AppConfigModel()
        self.load()

    def load(self):
        """Charge depuis le fichier JSON s'il existe."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Mise à jour partielle du modèle
                    self.settings = self.settings.model_copy(update=data)
                logger.debug("✅ Configuration dynamique chargée depuis settings.json")
            except Exception as e:
                logger.error(f"❌ Erreur lecture settings.json : {e}")
        else:
            logger.debug("ℹ️ Aucun settings.json trouvé, utilisation des variables d'environnement (Défaut).")
            # Sauvegarder immédiatement les valeurs par défaut
            self.save()

    def save(self):
        """Sauvegarde les paramètres actuels dans le fichier."""
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                f.write(self.settings.model_dump_json(indent=4))
        except Exception as e:
            logger.error(f"❌ Erreur écriture settings.json : {e}")

    def get_all(self):
        return self.settings.model_dump()
    
    def update(self, new_data: dict):
        """Met à jour les valeurs et sauvegarde."""
        self.settings = self.settings.model_copy(update=new_data)
        self.save()
        logger.info("⚙️ Paramètres dynamiques mis à jour et persistés.")

# Création du Singleton global
app_settings = ConfigManager()
