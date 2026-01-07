import os
from datetime import date
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURACIÓN DE BASE DE DATOS ---
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SERVER = os.getenv("DB_SERVER")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Variables de Alarma
DB_ALARMS = os.getenv("DB_ALARMS")
DB_USER_ALARMS = os.getenv("DB_USER_ALARMS")
DB_PASSWORD_ALARMS = os.getenv("DB_PASSWORD_ALARMS")
DB_SERVER_ALARMS = os.getenv("DB_SERVER_ALARMS")
DB_PORT_ALARMS = os.getenv("DB_PORT_ALARMS")

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- MODELO SQLALCHEMY ---
class Item(Base):
    __tablename__ = "clients_caporalsg"
    
    id = Column(Integer, primary_key=True, index=True)
    uniq_id = Column(String(100), index=True)
    name = Column(String(100))
    lastname = Column(String(100))
    personal_id = Column(String(50), unique=True, index=True)
    phone = Column(String(20))
    farm_name = Column(String(150))
    animal_limit = Column(Integer)
    name_db = Column(String(100))
    user_db = Column(String(100))
    port_db = Column(Integer)
    password_db = Column(String(255))
    server_db = Column(String(255))
    expiration_date = Column(Date)

# --- ESQUEMAS PYDANTIC ---
class ItemResponse(BaseModel):
    id: int
    uniq_id: str
    name: str
    lastname: str
    personal_id: str
    phone: Optional[str]
    farm_name: str
    animal_limit: int
    name_db: str
    user_db: str
    port_db: int
    server_db: str
    expiration_date: date
    # Añadimos los campos de alarmas al esquema de respuesta
    db_alarms: Optional[str] = None
    db_user_alarms: Optional[str] = None
    db_password_alarms: Optional[str] = None
    db_server_alarms: Optional[str] = None
    db_port_alarms: Optional[str] = None

    class Config:
        from_attributes = True

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Caporale SG API")

# Dependencia DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ENDPOINTS ---

@app.get("/get/{codigo}", response_model=ItemResponse)
def leer_item(codigo: str, db: Session = Depends(get_db)):
    # 1. Buscar el cliente en la base de datos
    resultado = db.query(Item).filter(Item.uniq_id == codigo).first()
    
    if not resultado:
        raise HTTPException(
            status_code=404, 
            detail=f"El código {codigo} no existe en el sistema"
        )
    
    # 2. Convertir el objeto de SQLAlchemy a un diccionario
    # Esto es necesario para mezclarlo con los datos de las variables de entorno
    item_data = {column.name: getattr(resultado, column.name) for column in resultado.__table__.columns}
    
    # 3. Inyectar las variables de alarmas en el diccionario de respuesta
    item_data["db_alarms"] = DB_ALARMS
    item_data["db_user_alarms"] = DB_USER_ALARMS
    item_data["db_password_alarms"] = DB_PASSWORD_ALARMS
    item_data["db_server_alarms"] = DB_SERVER_ALARMS
    item_data["db_port_alarms"] = DB_PORT_ALARMS
    
    return item_data