from datetime import datetime, timezone 
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text, DateTime, Float, Integer, String
from website.database.base import db

class Comments(db.Model):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())