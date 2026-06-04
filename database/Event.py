from datetime import datetime, timezone 
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text, DateTime, Float, Integer, String
from database.base import db


class Event(db.Model):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    event_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)

    genres: Mapped[str] = mapped_column(String(200), nullable=False)

    price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    tickets_available: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    overview: Mapped[str] = mapped_column(Text, nullable=False)

    # Assessment states: Open, Inactive, Sold Out, Cancelled
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="Open")

    # Store just a filename
    image_filename: Mapped[str] = mapped_column(String(200), nullable=True)

    # Acknowledgement of Country. Not an enum :P.
    acknowledgement_type: Mapped[str] = mapped_column(String(50), nullable=False, default="None")
    acknowledgement_city: Mapped[str] = mapped_column(String(120), nullable=True)
    traditional_custodians: Mapped[str] = mapped_column(String(200), nullable=True)
    acknowledgement_text: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    # Add booking and comment relationships here
    

    def update_status(self):
        """Update event status based on date and ticket availability."""
        if self.status == "Cancelled":
            return

        if self.event_datetime < datetime.now():
            self.status = "Inactive"
        elif self.tickets_available <= 0:
            self.status = "Sold Out"
        else:
            self.status = "Open"