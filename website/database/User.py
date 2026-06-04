from sqlalchemy.orm import Mapped, mapped_column
from website.database.base import db

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]

    email: Mapped[str] = mapped_column(unique=True)
    first_name: Mapped[str]
    surname: Mapped[str]
    phone_number: Mapped[int]
    address: Mapped[str]