import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.security import hash_password, verify_password


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_login = Column(DateTime(timezone=True), nullable=True)

    calculations = relationship(
        "Calculation",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def set_password(self, password: str) -> None:
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        return verify_password(password, self.password_hash)

    @classmethod
    def register(cls, db, user_in):
        existing = (
            db.query(cls)
            .filter((cls.username == user_in.username) | (cls.email == user_in.email))
            .first()
        )
        if existing:
            raise ValueError("Username or email already registered")

        user = cls(username=user_in.username, email=user_in.email)
        user.set_password(user_in.password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @classmethod
    def authenticate(cls, db, username: str, password: str):
        user = db.query(cls).filter(cls.username == username).first()
        if not user or not user.check_password(password):
            return None
        user.last_login = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)
        return user
