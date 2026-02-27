from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    # mapped_column is an actual column in the database
    # primary key is the unique identifier for each record
    # index=True allows faster lookups based on this column
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # nullable=False means it is a required field
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    password_hash : Mapped[str] = mapped_column(String(200), nullable=False) #200 characters good for argon2 hashing

    image_file: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        default=None,  
        # stores only the filename, not the actual file
        # decouples the database from the filesystem
        # could be replaced with a default image if desired
    

    )

    posts: Mapped[list[Post]] = relationship(back_populates="author", cascade="all, delete-orphan")
    # back_populates links two related models
    # so the relationship works both ways
    #cascade ensures that when a user is deleted, their posts are also deleted to maintain data integrity
    #orphan means if a post is removed from the user's posts list, it will be deleted from the database as well

    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/profile_pics/{self.image_file}"
        return "/static/profile_pics/default.jpg"


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    date_posted: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    author: Mapped[User] = relationship(back_populates="posts")
