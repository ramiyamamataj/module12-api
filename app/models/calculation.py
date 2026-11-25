import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    type = Column(String(50), nullable=False)
    inputs = Column(JSON, nullable=False)
    result = Column(Float, nullable=False)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="calculations")

    __mapper_args__ = {
        "polymorphic_identity": "calculation",
        "polymorphic_on": type,
    }

    def get_result(self) -> float:
        raise NotImplementedError("Subclasses must implement get_result()")

    @classmethod
    def create(cls, calc_type: str, inputs: list[float], user_id: uuid.UUID):
        normalized = calc_type.strip().lower()
        mapping = {
            "add": AddCalculation,
            "sub": SubCalculation,
            "subtract": SubCalculation,
            "multiply": MultiplyCalculation,
            "divide": DivideCalculation,
        }
        subclass = mapping.get(normalized)
        if not subclass:
            raise ValueError(f"Unsupported calculation type: {calc_type}")

        instance = subclass(inputs=inputs, user_id=user_id)
        instance.result = instance.get_result()
        return instance


class AddCalculation(Calculation):
    __mapper_args__ = {"polymorphic_identity": "add"}

    def get_result(self) -> float:
        return float(sum(self.inputs))


class SubCalculation(Calculation):
    __mapper_args__ = {"polymorphic_identity": "sub"}

    def get_result(self) -> float:
        total = float(self.inputs[0])
        for val in self.inputs[1:]:
            total -= float(val)
        return total


class MultiplyCalculation(Calculation):
    __mapper_args__ = {"polymorphic_identity": "multiply"}

    def get_result(self) -> float:
        total = 1.0
        for val in self.inputs:
            total *= float(val)
        return total


class DivideCalculation(Calculation):
    __mapper_args__ = {"polymorphic_identity": "divide"}

    def get_result(self) -> float:
        total = float(self.inputs[0])
        for val in self.inputs[1:]:
            if float(val) == 0.0:
                raise ValueError("Cannot divide by zero")
            total /= float(val)
        return total
