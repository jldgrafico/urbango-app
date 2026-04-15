from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class VehicleType(str, enum.Enum):
    car = "car"
    motorcycle = "motorcycle"
    van = "van"

class DriverProfile(Base):
    __tablename__ = "driver_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    license_number = Column(String(50), unique=True, nullable=False)
    vehicle_type = Column(Enum(VehicleType), nullable=False, default=VehicleType.car)
    vehicle_make = Column(String(50), nullable=False)
    vehicle_model = Column(String(50), nullable=False)
    vehicle_year = Column(Integer, nullable=False)
    vehicle_color = Column(String(30), nullable=False)
    plate_number = Column(String(20), unique=True, nullable=False)
    is_online = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    rating_avg = Column(Float, default=5.0)
    total_trips = Column(Integer, default=0)
    current_lat = Column(Float, nullable=True)
    current_lng = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="driver_profile")

    def __repr__(self):
        return f"<Driver {self.plate_number}>"