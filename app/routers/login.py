# app/login.py
import os
from datetime import date, datetime, timedelta, timezone
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.utils.db_tools import get_read_db, get_write_db
from app.utils.auth import verificar_password, crear_token_acceso, obtener_password_hash
from app.models.login import Usuario  # Asegúrate de que tu modelo esté en app.models.models o similar
from app.schemas.login import UsuarioLogin, UsuarioCreate, Mensaje
from app.config import ACCESS_TOKEN_COOKIE_MAX_AGE

logger = logging.getLogger("LOGIN y REGISTRO")

# 1. El router para rutas normales (/api/login/login, etc.)
router = APIRouter(
    prefix="/api/login",
    tags=["Login y Registro"]
)
templates = Jinja2Templates(directory="app/templates")


@router.post("/login")
def login(response: Response, usuario: UsuarioLogin, db: Session = Depends(get_read_db)):
    # 1. Buscar usuario por email
    db_user = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    
    # 2. Validar existencia y contraseña
    if not db_user or not verificar_password(usuario.password, db_user.password):
        logger.warning(f"Intento de login fallido para email: {usuario.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos."
        )
    
    # 3. Validar si está activo (activo >= 10 permite el acceso directo)
    if db_user.activo == 0:
        logger.warning(f"Intento de login con cuenta desactivada: ID_USUARIO[{db_user.idusuario}]")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta ha sido desactivada."
        )
    
    # Configuración de tiempos de la cookie
    max_age_segundos = int(os.getenv("ACCESS_TOKEN_COOKIE_MAX_AGE", ACCESS_TOKEN_COOKIE_MAX_AGE if 'ACCESS_TOKEN_COOKIE_MAX_AGE' in globals() else 2678400)) 
    fecha_final = datetime.now(timezone.utc) + timedelta(seconds=max_age_segundos)

    # 4. Crear el Token de Acceso
    access_token = crear_token_acceso(data={"sub": db_user.email}, expires_at=fecha_final)
    
    # 5. CREAR LA COOKIE
    response.set_cookie(
        key="access_token", 
        value=access_token, 
        httponly=True,   # No accesible desde JS
        max_age=max_age_segundos,
        expires=fecha_final, 
        samesite="lax",  # Protección CSRF básica
        secure=False     # Cambiar a True cuando tengas HTTPS/SSL en producción
    )

    logger.info(f"Inicio de sesión exitoso para ID_USUARIO[{db_user.idusuario}]")
    
    return {"message": "Login exitoso", "redirect": "/"}


@router.post("/logout")
def logout(response: Response):
    """Elimina la cookie de sesión"""
    response.delete_cookie("access_token")
    return {"message": "Sesión cerrada"}


@router.post("/registro", response_model=Mensaje)
def registrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_write_db)):
    # 1. Verificar si el email ya existe en la BBDD
    db_user = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    
    if db_user:
        logger.info(f"Intento de registro con email ya existente: ID_USUARIO[{db_user.idusuario}]")
        raise HTTPException(status_code=400, detail="El email ya está registrado.")
    
    # Manejar valor por defecto para email si viene vacío
    email_a_guardar = usuario.email if usuario.email and usuario.email.strip() != "" else "na@na.com"

    # 2. Crear usuario nuevo con acceso inmediato (activo=10, email_verificado=True)
    db_user = Usuario(
        nombre=usuario.nombre,
        email=email_a_guardar,
        password=obtener_password_hash(usuario.password),
        fechaCreacion=date.today(),
        activo=10,             # Acceso permitido directamente
        email_verificado=True  # Se mantiene el campo en la BBDD como se pidió
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    logger.info(f"Nuevo usuario registrado y activo automáticamente: ID_USUARIO[{db_user.idusuario}]")

    return {"message": "Usuario registrado correctamente. Ya puedes iniciar sesión."}
