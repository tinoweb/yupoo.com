from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from . import models
from .database import get_db
from .tasks import extract_yupoo_data
from datetime import datetime
from pydantic import BaseModel
import os
import shutil

router = APIRouter()

class ExtractionCreate(BaseModel):
    url: str

# Suporte para ambos os endpoints
# @router.post("/extractions/")
@router.post("/extraction/create")
def create_extraction(extraction: ExtractionCreate, db: Session = Depends(get_db)):
    try:
        # Log para debug
        print(f"Recebendo URL: {extraction.url}")
        
        # Criar nova extração no banco
        extraction_db = models.Extraction(
            url=extraction.url,
            status="pending",
            created_at=datetime.utcnow()
        )
        db.add(extraction_db)
        db.commit()
        db.refresh(extraction_db)
        
        # Iniciar tarefa em background
        extract_yupoo_data.delay(extraction.url, extraction_db.id)
        
        return {
            "message": "Extração iniciada com sucesso",
            "extraction_id": extraction_db.id,
            "status": extraction_db.status
        }
    except Exception as e:
        print(f"Erro ao criar extração: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/extraction/{extraction_id}")
def delete_extraction(extraction_id: int, db: Session = Depends(get_db)):
    extraction = db.query(models.Extraction).filter(models.Extraction.id == extraction_id).first()
    if not extraction:
        raise HTTPException(status_code=404, detail="Extração não encontrada")
    
    db.delete(extraction)
    db.commit()
    return {"message": "Extração removida com sucesso"}


@router.delete("/extractions/{extraction_id}/remove_folder/{folder_name}")
def remove_folder(extraction_id: int, folder_name: str, db: Session = Depends(get_db)):
    # Busca a extração no banco de dados
    extraction = db.query(models.Extraction).filter(models.Extraction.id == extraction_id).first()
    if not extraction:
        raise HTTPException(status_code=404, detail="Extração não encontrada")
    
    # Obtém o caminho da pasta principal (result_path)
    main_folder_path = extraction.result_path
    if not main_folder_path or not os.path.exists(main_folder_path):
        raise HTTPException(status_code=404, detail="Pasta principal não encontrada ou caminho inválido")
    
    # Cria o caminho completo da pasta que será deletada
    folder_path = os.path.join(main_folder_path, folder_name)
    if not os.path.exists(folder_path):
        raise HTTPException(status_code=404, detail=f"Pasta '{folder_name}' não encontrada dentro da pasta principal")
    
    try:
        # Remove a pasta e todo o seu conteúdo
        shutil.rmtree(folder_path)
        return {"message": f"Pasta '{folder_name}' removida com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover a pasta '{folder_name}': {str(e)}")


@router.get("/extraction/{extraction_id}")
def get_extraction_status(extraction_id: int, db: Session = Depends(get_db)):
    """
    Retorna o status de uma extração
    """
    extraction = db.query(models.Extraction).filter(models.Extraction.id == extraction_id).first()
    if not extraction:
        raise HTTPException(status_code=404, detail="Extração não encontrada")
    
    return {
        "id": extraction.id,
        "url": extraction.url,
        "status": extraction.status,
        "created_at": extraction.created_at,
        "started_at": extraction.started_at,
        "completed_at": extraction.completed_at,
        "error_message": extraction.error_message,
        "result_path": extraction.result_path
    }

@router.get("/api/status")
async def status():
    return {"message": "API is working"}
