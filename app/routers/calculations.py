import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.calculation import Calculation
from app.models.user import User
from app.schemas.calculation import (
    CalculationCreate,
    CalculationRead,
    CalculationUpdate,
)
from app.security import get_current_user

router = APIRouter(prefix="/calculations", tags=["Calculations"])


@router.post("", response_model=CalculationRead, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=CalculationRead, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def add_calculation(
    calc_in: CalculationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        calc = Calculation.create(
            calc_type=calc_in.type.value,
            inputs=calc_in.inputs,
            user_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    db.add(calc)
    db.commit()
    db.refresh(calc)
    return calc


@router.get("", response_model=List[CalculationRead])
@router.get("/", response_model=List[CalculationRead], include_in_schema=False)
def browse_calculations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Calculation)
        .filter(Calculation.user_id == current_user.id)
        .order_by(Calculation.created_at.desc())
        .all()
    )


@router.get("/{calc_id}", response_model=CalculationRead)
def read_calculation(
    calc_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    calc = (
        db.query(Calculation)
        .filter(Calculation.id == calc_id, Calculation.user_id == current_user.id)
        .first()
    )
    if not calc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found",
        )
    return calc


@router.put("/{calc_id}", response_model=CalculationRead)
def edit_calculation(
    calc_id: uuid.UUID,
    calc_in: CalculationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    calc = (
        db.query(Calculation)
        .filter(Calculation.id == calc_id, Calculation.user_id == current_user.id)
        .first()
    )
    if not calc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found",
        )

    new_type = calc_in.type.value if calc_in.type is not None else calc.type
    new_inputs = calc_in.inputs if calc_in.inputs is not None else calc.inputs

    try:
        recomputed = Calculation.create(
            calc_type=new_type,
            inputs=new_inputs,
            user_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    calc.type = recomputed.type
    calc.inputs = recomputed.inputs
    calc.result = recomputed.result
    db.commit()
    db.expire_all()

    return (
        db.query(Calculation)
        .filter(Calculation.id == calc_id, Calculation.user_id == current_user.id)
        .first()
    )


@router.delete("/{calc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation(
    calc_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    calc = (
        db.query(Calculation)
        .filter(Calculation.id == calc_id, Calculation.user_id == current_user.id)
        .first()
    )
    if not calc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found",
        )

    db.delete(calc)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
