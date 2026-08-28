import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


TEST_DB = Path(tempfile.gettempdir()) / "fiche_pedagogique_mvp_tests.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.seed import seed_database  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_database(session)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

