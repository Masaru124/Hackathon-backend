from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable is not set")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # PostgreSQL with connection pooling and SSL support
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,          # Maintain 5 persistent connections
        max_overflow=10,      # Allow up to 10 additional connections under load
        pool_recycle=1800,    # Recycle connections every 30 minutes to avoid timeout
        pool_pre_ping=True,   # Verify connection health before use
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

