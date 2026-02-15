from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from datetime import datetime
import enum
from backend.database import Base

class PostStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    ERROR = "ERROR"

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String, nullable=False)
    caption = Column(Text, nullable=True)
    status = Column(String, default=PostStatus.PENDING.value)
    attempts = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
