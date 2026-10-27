# app/core/security.py

import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.config import ADMIN_USER, ADMIN_PASSWORD
import logging 

logger = logging.getLogger("SECURITY")

security = HTTPBasic()

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    # Comparamos de forma segura para evitar ataques de tiempo (timing attacks)
    is_user_ok = secrets.compare_digest(credentials.username, ADMIN_USER)
    is_pass_ok = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    
    if not (is_user_ok and is_pass_ok):
        logger.warning(f"Intento de acceder al panel de Administración inválido: {credentials.username} - {credentials.password}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de administrador incorrectas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username