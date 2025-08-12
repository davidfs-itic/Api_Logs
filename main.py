# main.py
from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel, ValidationError
from typing import List, Optional
from datetime import datetime

# Importa les funcions del nostre fitxer db.py
import db

# --- Validació inicial de la base de dades ---
db.setup_database()

# --- Esquemes Pydantic ---
class LogCreate(BaseModel):
    user: str
    long_text: str

class LogResponse(BaseModel):
    id: int
    timestamp: datetime
    user: str
    long_text: str

# --- Instància de l'aplicació FastAPI ---
app = FastAPI()

# --- Endpoints de l'API ---
@app.post("/logs/", status_code=status.HTTP_201_CREATED, response_model=LogResponse)
def create_log(log: LogCreate):
    """
    Crea un nou registre de log.
    """
    new_log = db.create_log_entry(user=log.user, long_text=log.long_text)
    if not new_log:
        raise HTTPException(status_code=500, detail="El registre no s'ha pogut crear.")
    return new_log

@app.get("/logs/user/{user}", response_model=List[LogResponse])
def get_logs_by_user_endpoint(user: str):
    """
    Obté tots els logs d'un usuari específic.
    """
    logs = db.get_logs_by_user(user)
    if not logs:
        raise HTTPException(status_code=404, detail="No s'han trobat logs per a aquest usuari.")
    return logs

@app.get("/logs/user/{user}/search", response_model=List[LogResponse])
def search_logs_by_user_and_time(
    user: str,
    start_time: Optional[datetime] = Query(None, description="Data i hora d'inici (format ISO 8601)"),
    end_time: Optional[datetime] = Query(None, description="Data i hora de finalització (format ISO 8601)")
):
    """
    Cerca logs d'un usuari dins d'un rang de temps.
    """
    if start_time and end_time:
        if start_time > end_time:
            raise HTTPException(status_code=400, detail="La data d'inici ha de ser anterior a la de finalització.")
        
        logs = db.get_logs_by_user_and_time(user, start_time, end_time)
    else:
        # Si no es proporcionen dates, es comporta com la cerca per usuari
        logs = db.get_logs_by_user(user)

    if not logs:
        raise HTTPException(status_code=404, detail="No s'han trobat logs amb aquests criteris.")
    return logs