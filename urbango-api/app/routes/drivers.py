from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.driver import DriverProfile
from app.dependencies import get_current_user, get_current_driver
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/drivers", tags=["Conductores"])

class DriverProfileCreate(BaseModel):
    license_number: str
    vehicle_type: str = "car"
    vehicle_make: str
    vehicle_model: str
    vehicle_year: int
    vehicle_color: str
    plate_number: str

class DriverProfileResponse(BaseModel):
    id: int
    license_number: str
    vehicle_type: str
    vehicle_make: str
    vehicle_model: str
    vehicle_year: int
    vehicle_color: str
    plate_number: str
    is_online: bool
    is_verified: bool
    rating_avg: float
    total_trips: int

    class Config:
        from_attributes = True

@router.post("/profile", response_model=DriverProfileResponse, status_code=201)
def create_driver_profile(
    profile_data: DriverProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verificar que no tenga perfil ya
    existing = db.query(DriverProfile).filter(
        DriverProfile.user_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya tienes un perfil de conductor")

    # Verificar placa única
    existing_plate = db.query(DriverProfile).filter(
        DriverProfile.plate_number == profile_data.plate_number
    ).first()
    if existing_plate:
        raise HTTPException(status_code=400, detail="Esta placa ya está registrada")

    profile = DriverProfile(
        user_id=current_user.id,
        **profile_data.dict()
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

@router.get("/profile", response_model=DriverProfileResponse)
def get_driver_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(DriverProfile).filter(
        DriverProfile.user_id == current_user.id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil de conductor no encontrado")
    return profile

@router.patch("/status")
def update_online_status(
    is_online: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(DriverProfile).filter(
        DriverProfile.user_id == current_user.id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil de conductor no encontrado")

    profile.is_online = is_online
    db.commit()
    return {"message": f"Estado actualizado: {'online' if is_online else 'offline'}"}