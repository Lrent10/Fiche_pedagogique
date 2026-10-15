from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings


class Base(DeclarativeBase):
    pass


# Sécurité absolue : s'assurer que le dossier de la base SQLite existe avant la connexion
if settings.database_url.startswith("sqlite:///"):
    sqlite_raw_path = settings.database_url.replace("sqlite:///", "")
    Path(sqlite_raw_path).parent.mkdir(parents=True, exist_ok=True)

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, future=True)


if settings.database_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
