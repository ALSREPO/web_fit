import os
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.config import SECRET_KEY, ALGORITHM
from app.models.login import Usuario
from app.utils.db_tools import get_read_db

# Configuración de Passlib para usar SHA-512
pwd_context = CryptContext(schemes=["sha512_crypt"], deprecated="auto")

logger = logging.getLogger("DIARIO-HIERRO-auth")


def verificar_password(plain_password, hashed_password):
    """Compara la contraseña en plano con el hash de la BBDD"""
    return pwd_context.verify(plain_password, hashed_password)


def obtener_password_hash(password):
    """Genera el hash SHA-512 de una contraseña"""
    return pwd_context.hash(password)


def crear_token_acceso(data: dict, expires_at: Optional[datetime] = None):
    """Genera un token JWT firmado usando una fecha de expiración absoluta"""
    to_encode = data.copy()
    
    if expires_at:
        expire = expires_at
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def obtener_token_de_cookie(request: Request):
    """Extrae el token JWT de la cookie llamada 'access_token'."""
    return request.cookies.get("access_token")


def validar_token(token: str):
    """Decodifica y valida el token. Devuelve el email si es válido."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None


async def obtener_usuario_actual(request: Request, db: Session = Depends(get_read_db)):
    token = obtener_token_de_cookie(request)
    if not token:
        return None
    
    email = validar_token(token)
    if not email:
        return None
        
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if not user or user.activo < 1:
        return None
    return user 


async def verificar_admin(user: Usuario = Depends(obtener_usuario_actual)):
    if not user or user.activo < 2:
        logger.warning(f"Intento de acceso no autorizado a ruta admin por parte de ID_USUARIO[{user.idusuario if user else 'usuario desconocido'}]")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requieren permisos de administrador"
        )
    return user


async def usuario_obligatorio(user: Usuario = Depends(obtener_usuario_actual)):
    if not user or user.activo < 1:
        logger.warning(f"Intento de acceso no autorizado por parte de ID_USUARIO[{user.idusuario if user else 'usuario desconocido'}]")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requiere estar logueado"
        )
    return userpip