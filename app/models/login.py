from sqlalchemy import Column, Integer, String, Date, Boolean
from app.utils.db_tools import Base

# --- Clases Principales ---

class Usuario(Base):
    __tablename__ = "ta_usuarios"
    
    idusuario = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    password = Column(String(200), nullable=False)
    fechaCreacion = Column(Date, nullable=False)
    email = Column(String(60), nullable=False, default="na@na.com")
    activo = Column(Integer, nullable=False, default=10)        # 10 por defecto para acceso directo
    email_verificado = Column(Boolean, default=True)           # Se mantiene en BBDD como pediste