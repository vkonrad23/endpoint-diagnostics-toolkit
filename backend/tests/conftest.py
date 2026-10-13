import os,tempfile
os.environ["EDST_DATABASE_URL"]="sqlite:///./test-edst.db"
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import Base,engine
@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(engine); Base.metadata.create_all(engine); yield
@pytest.fixture
def client(): return TestClient(app)
