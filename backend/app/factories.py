from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models, schemas
from .auth import get_current_user

router = APIRouter(prefix="/factories", tags=["Factories"])


# 🔹 DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🏭 ADD FACTORY
@router.post("/", response_model=schemas.FactoryResponse)
def add_factory(
    factory: schemas.FactoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_factory = models.Factory(
        name=factory.name,
        address=factory.address,
        owner_id=current_user.id,
    )
    db.add(db_factory)
    db.commit()
    db.refresh(db_factory)
    return db_factory


# 📋 LIST FACTORIES (user-wise)
@router.get("/", response_model=list[schemas.FactoryResponse])
def list_factories(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    factories = (
        db.query(models.Factory)
        .filter(models.Factory.owner_id == current_user.id)
        .all()
    )
    return factories


# ❌ DELETE FACTORY (optional but safe)
@router.delete("/{factory_id}")
def delete_factory(
    factory_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    factory = (
        db.query(models.Factory)
        .filter(
            models.Factory.id == factory_id,
            models.Factory.owner_id == current_user.id,
        )
        .first()
    )

    if not factory:
        raise HTTPException(status_code=404, detail="Factory not found")

    db.delete(factory)
    db.commit()
    return {"message": "Factory deleted successfully"}
