from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import config

# Create engine
engine = create_engine(config.DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
