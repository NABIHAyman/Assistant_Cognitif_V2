# backend/app/models.py
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# 1. Configuration de SQLite (Le fichier cognition.db sera créé automatiquement)
SQLALCHEMY_DATABASE_URL = "sqlite:////app/data/cognition.db"

# L'argument check_same_thread=False est spécifique à SQLite pour fonctionner avec FastAPI (asynchrone)
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 2. Notre Table "Propositions"
class Proposition(Base):
    __tablename__ = "propositions"

    id = Column(Integer, primary_key=True, index=True)

    action = Column(String)  # 'create', 'append', 'ignore'
    target_file = Column(String, nullable=True)  # Chemin relatif pour 'append'
    source_image = Column(String, nullable=True)  # Traçabilité du Batch

    domain = Column(String)
    is_new_domain = Column(Boolean, default=False)
    existing_tags = Column(String)  # Séparés par des virgules
    proposed_new_tags = Column(String)

    title = Column(String, index=True)
    markdown_content = Column(Text)
    reasoning = Column(Text) # Pourquoi l'IA a fait ce choix
    status = Column(String, default="pending") # Valeurs: pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)

# 3. Création automatique des tables si elles n'existent pas
Base.metadata.create_all(bind=engine)

# 4. Dépendance FastAPI pour obtenir la session de la base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()