import uuid
import pytest
from app.models.calculation import (
    AddCalculation,
    Calculation,
    DivideCalculation,
    MultiplyCalculation,
    SubCalculation,
)
from app.security import create_access_token, hash_password, verify_password


def test_password_hashing_and_verification():
    hashed = hash_password("SecurePass123!")
    assert hashed != "SecurePass123!"
    assert verify_password("SecurePass123!", hashed) is True
    assert verify_password("WrongPass!", hashed) is False


def test_jwt_token_creation():
    user_id = str(uuid.uuid4())
    token = create_access_token({"sub": user_id, "username": "tester"})
    assert isinstance(token, str)
    assert len(token) > 20


def test_calculation_factory_operations():
    uid = uuid.uuid4()
    add_c = Calculation.create("add", [10, 5, 2], uid)
    assert isinstance(add_c, AddCalculation)
    assert add_c.result == 17.0

    sub_c = Calculation.create("subtract", [20, 5, 3], uid)
    assert isinstance(sub_c, SubCalculation)
    assert sub_c.result == 12.0

    mul_c = Calculation.create("multiply", [4, 5], uid)
    assert isinstance(mul_c, MultiplyCalculation)
    assert mul_c.result == 20.0

    div_c = Calculation.create("divide", [20, 4], uid)
    assert isinstance(div_c, DivideCalculation)
    assert div_c.result == 5.0


def test_calculation_factory_errors():
    uid = uuid.uuid4()
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        Calculation.create("divide", [10, 0], uid)

    with pytest.raises(ValueError, match="Unsupported calculation type"):
        Calculation.create("modulo", [10, 3], uid)
