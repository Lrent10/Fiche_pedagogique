import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


TEST_DB = Path(tempfile.mkdtemp(prefix="fichemaths_tests_")) / "tests.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ["EXPORT_DIR"] = str(TEST_DB.parent / "exports")

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.seed import seed_database  # noqa: E402
from app.config import settings  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_database():
    previous_key = settings.package_import_key
    settings.package_import_key = "test-package-key"
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_database(session)
    yield
    Base.metadata.drop_all(bind=engine)
    settings.package_import_key = previous_key


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
