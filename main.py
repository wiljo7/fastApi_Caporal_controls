import os
from datetime import date
from typing import List, Optional

# 1. Importaciones de FastAPI y SQLAlchemy
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# 2. Cargar variables de entorno desde el archivo .env
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SERVER = os.getenv("DB_SERVER")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# 3. Configuración de la URL de conexión para MySQL
# La cadena usa pymysql para comunicarse con la instancia externa
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

# Creamos el engine con pool_pre_ping para evitar desconexiones de la BD externa
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 4. Modelo de la Tabla (SQLAlchemy)
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

# 5. Esquema de Respuesta (Pydantic) para formatear el JSON de salida
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

    class Config:
        from_attributes = True

# Creamos las tablas si no existen (solo si tienes permisos en esa BD)
Base.metadata.create_all(bind=engine)

# 6. Inicialización de FastAPI
app = FastAPI(title="Caporale SG API")

# Dependencia para la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 7. Endpoints
#@app.get("/")
#def read_root():
#    return {"message": "API de Clientes funcionando correctamente"}

#@app.get("/all", response_model=List[ItemResponse])
#def read_all(db: Session = Depends(get_db)):
#    return db.query(Item).all()

@app.get("/get/{codigo}", response_model=ItemResponse)
def leer_item(codigo: str, db: Session = Depends(get_db)):
    # Buscamos por el campo uniq_id que envias desde el cliente
    resultado = db.query(Item).filter(Item.uniq_id == codigo).first()
    
    if not resultado:
        raise HTTPException(
            status_code=404, 
            detail=f"El código {codigo} no existe en el sistema"
        )
    
    return resultado