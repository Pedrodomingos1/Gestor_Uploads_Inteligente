import logging
import os
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from backend import models, schemas, services
from backend.database import engine, get_db

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Logging Configuration
logging.basicConfig(
    handlers=[RotatingFileHandler('logs/app.log', maxBytes=100000, backupCount=5)],
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="InstaAuto Backend")

@app.post("/agendar", response_model=schemas.PostResponse, status_code=202)
def create_post(post: schemas.PostCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    logger.info(f"Received scheduling request for {post.image_path}")

    db_post = models.Post(
        image_path=post.image_path,
        caption=post.caption,
        status=models.PostStatus.PENDING.value
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    background_tasks.add_task(services.process_upload, db_post.id)

    return db_post

@app.get("/posts", response_model=list[schemas.PostResponse])
def read_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    posts = db.query(models.Post).order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all()
    return posts

class TokenUpdate(schemas.BaseModel):
    token: str

@app.post("/admin/token")
def update_token(data: TokenUpdate):
    services.instagram_service.update_token(data.token)
    return {"status": "Token updated"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
