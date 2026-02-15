import os
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app, get_db
from backend.database import Base

# Setup Test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./backend/tests/test.db"
os.makedirs("./backend/tests", exist_ok=True)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./backend/tests/test.db"):
        os.remove("./backend/tests/test.db")

def test_create_post(setup_db):
    with patch("backend.services.process_upload") as mock_task:
        response = client.post(
            "/agendar",
            json={"image_path": "test_image.jpg", "caption": "Test Caption"}
        )
        assert response.status_code == 202
        data = response.json()
        assert data["image_path"] == "test_image.jpg"
        assert data["status"] == "PENDING"
        assert "id" in data

        # Verify background task was added
        # Note: TestClient runs background tasks, but we patched it so it won't execute the real function
        # However, the mock should be called?
        # FastAPIs TestClient executes background tasks. Since we patched `backend.services.process_upload`
        # inside the `with` block, when `background_tasks.add_task` runs, it calls the mock.
        # Wait, `add_task` adds the function to be called later.
        # `TestClient` calls it after response.
        # So yes, mock_task should be called.
        # Actually, `add_task` stores the function object.
        # `app.post` calls `add_task(services.process_upload, ...)`
        # If we patch `backend.services.process_upload`, `services.process_upload` in `main.py`
        # refers to the mocked object if `backend.main` imported it as `from backend import services`.
        # Yes, `main.py` has `from backend import services`.
        # So `services.process_upload` will be the mock.
        mock_task.assert_called_once()

def test_read_posts(setup_db):
    # Create a dummy post
    db = TestingSessionLocal()
    from backend.models import Post
    db_post = Post(image_path="read_test.jpg", status="DONE")
    db.add(db_post)
    db.commit()
    db.close()

    response = client.get("/posts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["image_path"] == "read_test.jpg"
