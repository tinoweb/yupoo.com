from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from . import models, auth
from .database import get_db
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional
import hashlib
from datetime import datetime

router = APIRouter()

# Middleware para verificar se o usuário está autenticado e é administrador
async def admin_required(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        print("Token não encontrado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Remover o prefixo "Bearer " se existir
        if token.startswith("Bearer "):
            token = token.replace("Bearer ", "")
        
        print(f"Verificando token: {token}")
        user = await auth.get_current_user(token, db)
        
        if not user:
            print("Usuário não encontrado")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        
        if not user.is_admin:
            print(f"Usuário {user.username} não é administrador")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not an administrator",
            )
        
        print(f"Usuário admin autenticado: {user.username}")
        return user
    except Exception as e:
        print(f"Erro na autenticação: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication error",
        )

# Configurar os templates com os diretórios corretos
templates = Jinja2Templates(directory="templates")
templates.env.loader.searchpath.append("app/admin")

# Adicionar filtro md5 para o Gravatar
def md5_filter(value):
    if not value:
        return ""
    return hashlib.md5(value.encode('utf-8')).hexdigest()

templates.env.filters["md5"] = md5_filter

@router.get("/admin", response_class=HTMLResponse)
@router.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user: models.User = Depends(admin_required)
):
    # Obter estatísticas para o dashboard
    total_users = db.query(models.User).count()
    total_extractions = db.query(models.Extraction).count()
    recent_extractions = db.query(models.Extraction).order_by(models.Extraction.created_at.desc()).limit(5).all()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "total_users": total_users,
        "total_extractions": total_extractions,
        "recent_extractions": recent_extractions,
        "now": datetime.now()
    })

@router.get("/admin/users", response_class=HTMLResponse)
async def admin_users_page(
    request: Request,
    db: Session = Depends(get_db),
    user: models.User = Depends(admin_required)
):
    users = db.query(models.User).all()
    return templates.TemplateResponse("users.html", {
        "request": request,
        "users": users,
        "user": user
    })

@router.post("/admin/users/{user_id}/toggle-admin")
async def toggle_admin_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(admin_required)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Não permitir que o admin remova seus próprios privilégios
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot remove your own admin privileges")
    
    user.is_admin = not user.is_admin
    db.commit()
    return {"success": True, "is_admin": user.is_admin}

@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(admin_required)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Não permitir que o admin exclua sua própria conta
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    db.delete(user)
    db.commit()
    return {"success": True}

@router.get("/admin/extractions", response_class=HTMLResponse)
async def admin_extractions_page(
    request: Request,
    page: int = 1,
    per_page: int = 10,
    db: Session = Depends(get_db),
    user: models.User = Depends(admin_required)
):
    # Paginação das extrações
    offset = (page - 1) * per_page
    total = db.query(models.Extraction).count()
    extractions = db.query(models.Extraction).order_by(
        models.Extraction.created_at.desc()
    ).offset(offset).limit(per_page).all()
    
    return templates.TemplateResponse("extractions.html", {
        "request": request,
        "user": user,
        "extractions": extractions,
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": (total + per_page - 1) // per_page
    })

@router.get("/admin/settings", response_class=HTMLResponse)
async def admin_settings_page(
    request: Request,
    user: models.User = Depends(admin_required)
):
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "user": user,
        "now": datetime.now()
    })

@router.post("/admin/settings")
async def update_settings(
    request: Request,
    extraction_limit: Optional[int] = Form(None),
    concurrent_extractions: Optional[int] = Form(None),
    user: models.User = Depends(admin_required),
    db: Session = Depends(get_db)
):
    # Aqui você pode implementar a lógica para salvar as configurações
    # Por exemplo, salvando em um modelo Settings no banco de dados
    return RedirectResponse(url="/admin/settings", status_code=status.HTTP_302_FOUND)
