import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CalculationType(str, Enum):
    add = "add"
    sub = "sub"
    subtract = "subtract"
    multiply = "multiply"
    divide = "divide"


def _normalize_type(value):
    if isinstance(value, str):
        cleaned = value.strip().lower()
        if cleaned == "subtract":
            return "sub"
        return cleaned
    return value


class CalculationBase(BaseModel):
    type: CalculationType
    inputs: List[float] = Field(..., min_length=2)

    @field_validator("type", mode="before")
    @classmethod
    def clean_type(cls, v):
        return _normalize_type(v)

    @model_validator(mode="after")
    def validate_division(self):
        if self.type == CalculationType.divide:
            if any(x == 0 for x in self.inputs[1:]):
                raise ValueError("Cannot divide by zero")
        return self


class CalculationCreate(CalculationBase):
    pass


class CalculationUpdate(BaseModel):
    type: Optional[CalculationType] = None
    inputs: Optional[List[float]] = Field(default=None, min_length=2)

    @field_validator("type", mode="before")
    @classmethod
    def clean_type(cls, v):
        if v is None:
            return v
        return _normalize_type(v)

    @model_validator(mode="after")
    def validate_update(self):
        if self.type == CalculationType.divide and self.inputs is not None:
            if any(x == 0 for x in self.inputs[1:]):
                raise ValueError("Cannot divide by zero")
        return self


class CalculationRead(BaseModel):
    id: uuid.UUID
    type: str
    inputs: List[float]
    result: float
    user_id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
