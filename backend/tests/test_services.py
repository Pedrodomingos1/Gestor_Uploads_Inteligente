import os
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend import models, services

# Setup Test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./backend/tests/test_services.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db_session():
    models.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    models.Base.metadata.drop_all(bind=engine)
    if os.path.exists("./backend/tests/test_services.db"):
        os.remove("./backend/tests/test_services.db")

def test_process_upload_success(db_session):
    # Create a post
    post = models.Post(image_path="service_test.jpg", status=models.PostStatus.PENDING.value)
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)

    # Patch SessionLocal inside services.py to use our test DB session factory
    with patch("backend.services.SessionLocal", side_effect=TestingSessionLocal):
        with patch("backend.services.instagram_service.post_image") as mock_insta:
            with patch("backend.services.ai_service.generate_caption", return_value="AI Caption"):

                services.process_upload(post.id)

                # Check DB update
                # We need to refresh or query again.
                # Since process_upload used a different session (TestingSessionLocal creates new session),
                # the changes are committed to the DB.
                # db_session needs to expire_all or query freshly.
                db_session.expire_all()
                updated_post = db_session.query(models.Post).filter(models.Post.id == post.id).first()
                assert updated_post.status == models.PostStatus.DONE.value
                assert updated_post.caption == "AI Caption"
                mock_insta.assert_called_once()

def test_process_upload_failure(db_session):
    # Create a post
    post = models.Post(image_path="fail_test.jpg", status=models.PostStatus.PENDING.value)
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)

    with patch("backend.services.SessionLocal", side_effect=TestingSessionLocal):
        with patch("backend.services.instagram_service.post_image", side_effect=Exception("Upload Failed")):
             with patch("backend.services.ai_service.generate_caption", return_value="AI Caption"):

                services.process_upload(post.id)

                db_session.expire_all()
                updated_post = db_session.query(models.Post).filter(models.Post.id == post.id).first()
                assert updated_post.status == models.PostStatus.ERROR.value
                assert "Upload Failed" in updated_post.error_message
