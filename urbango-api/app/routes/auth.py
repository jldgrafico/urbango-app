from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.auth import verify_password, get_password_hash, create_access_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Verificar si el teléfono ya existe
    existing = db.query(User).filter(User.phone == user_data.phone).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Este número de teléfono ya está registrado"
        )

    # Verificar email si fue proporcionado
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="Este correo ya está registrado"
            )

    # Crear usuario
    new_user = User(
        full_name=user_data.full_name,
        phone=user_data.phone,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        status=UserStatus.active
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    # Buscar usuario por teléfono
    user = db.query(User).filter(User.phone == credentials.phone).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Teléfono o contraseña incorrectos"
        )

    # Verificar contraseña
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Teléfono o contraseña incorrectos"
        )

    # Verificar estado
    if user.status == UserStatus.suspended:
        raise HTTPException(
            status_code=403,
            detail="Tu cuenta está suspendida"
        )

    # Generar token
    token = create_access_token({"sub": str(user.id), "role": user.role})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
def get_me(db: Session = Depends(get_db)):
    # Este endpoint lo completamos cuando agreguemos el middleware de autenticación
    pass