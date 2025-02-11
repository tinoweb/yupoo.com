from fastapi import FastAPI, Depends, HTTPException, status, Request, Form, Response, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from sqlalchemy.orm import Session
from datetime import timedelta
from . import models, schemas, auth
from .database import engine, get_db
import os
import shutil
import tempfile
from typing import Optional

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Yupoo Extractor")

# Configuração de templates e arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/files", StaticFiles(directory="extractions"), name="extractions_files")
templates = Jinja2Templates(directory="templates")

# Middleware para verificar autenticação em páginas web
async def get_current_user_from_session(request: Request, db: Session = Depends(get_db)) -> Optional[models.User]:
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        user = await auth.get_current_user(token, db)
        return user
    except:
        return None

# Endpoint de healthcheck
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, user: Optional[models.User] = Depends(get_current_user_from_session)):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, user: Optional[models.User] = Depends(get_current_user_from_session)):
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    form_data = OAuth2PasswordRequestForm(username=username, password=password, scope="")
    try:
        token_data = await login_for_access_token(form_data, db)
        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="access_token", value=token_data["access_token"], httponly=True)
        return response
    except HTTPException:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Usuário ou senha inválidos"}
        )

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, user: Optional[models.User] = Depends(get_current_user_from_session)):
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        user_data = schemas.UserCreate(email=email, username=username, password=password)
        create_user(user_data, db)
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    except HTTPException as e:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": e.detail}
        )

@app.get("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response

@app.get("/extractions", response_class=HTMLResponse)
async def list_extractions_page(
    request: Request,
    user: Optional[models.User] = Depends(get_current_user_from_session),
    db: Session = Depends(get_db)
):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    extractions = db.query(models.Extraction).filter(
        models.Extraction.user_id == user.id
    ).all()
    
    return templates.TemplateResponse(
        "extractions.html",
        {"request": request, "user": user, "extractions": extractions}
    )

@app.post("/extractions/", response_class=HTMLResponse)
async def create_extraction_web(
    request: Request,
    url: str = Form(...),
    user: Optional[models.User] = Depends(get_current_user_from_session),
    db: Session = Depends(get_db)
):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    extraction = models.Extraction(
        url=url,
        status="pending",
        user_id=user.id
    )
    db.add(extraction)
    db.commit()
    db.refresh(extraction)
    
    # Inicia o processo de extração em background
    try:
        from . import scraper
        scraper.process_extraction(extraction, db)
    except Exception as e:
        print(f"Erro na extração: {e}")
    
    return RedirectResponse(url="/extractions", status_code=status.HTTP_302_FOUND)

@app.get("/extractions/{extraction_id}/view", response_class=HTMLResponse)
async def view_extraction(
    request: Request,
    extraction_id: int,
    user: Optional[models.User] = Depends(get_current_user_from_session),
    db: Session = Depends(get_db)
):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    extraction = db.query(models.Extraction).filter(
        models.Extraction.id == extraction_id,
        models.Extraction.user_id == user.id
    ).first()
    
    if not extraction:
        raise HTTPException(status_code=404, detail="Extração não encontrada")
    
    # Verifica se há um diretório de resultados
    if not extraction.result_path or not os.path.exists(extraction.result_path):
        raise HTTPException(status_code=404, detail="Diretório de resultados não encontrado")

    # Lista apenas as pastas principais (álbuns)
    folders = []
    for item in os.listdir(extraction.result_path):
        item_path = os.path.join(extraction.result_path, item)
        if os.path.isdir(item_path):
            folders.append({
                'name': item,
                'path': item,
                'size': sum(os.path.getsize(os.path.join(dirpath, filename))
                           for dirpath, dirnames, filenames in os.walk(item_path)
                           for filename in filenames)
            })

    return templates.TemplateResponse(
        "extraction_details.html",
        {
            "request": request,
            "extraction": extraction,
            "folders": folders
        }
    )

@app.get("/extractions/{extraction_id}/download/{album_folder}")
async def download_album(
    extraction_id: int,
    album_folder: str,
    user: Optional[models.User] = Depends(get_current_user_from_session),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    extraction = db.query(models.Extraction).filter(
        models.Extraction.id == extraction_id,
        models.Extraction.user_id == user.id
    ).first()
    
    if not extraction or not extraction.result_path:
        raise HTTPException(status_code=404, detail="Extração não encontrada")
    
    album_path = os.path.join(extraction.result_path, album_folder)
    if not os.path.exists(album_path):
        raise HTTPException(status_code=404, detail="Álbum não encontrado")
    
    # Cria um arquivo ZIP temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
        # Cria o arquivo ZIP com o conteúdo do álbum
        shutil.make_archive(tmp_file.name[:-4], 'zip', album_path)
        
        # Retorna o arquivo ZIP para download
        return FileResponse(
            tmp_file.name,
            media_type='application/zip',
            filename=f'{album_folder}.zip',
            background=background_tasks.add_task(os.unlink, tmp_file.name)
        )

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/extractions/", response_model=schemas.Extraction)
def create_extraction(
    extraction: schemas.ExtractionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_extraction = models.Extraction(
        url=extraction.url,
        status="pending",
        user_id=current_user.id
    )
    db.add(db_extraction)
    db.commit()
    db.refresh(db_extraction)
    return db_extraction

@app.get("/extractions/", response_model=list[schemas.Extraction])
def list_extractions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    extractions = db.query(models.Extraction).filter(
        models.Extraction.user_id == current_user.id
    ).all()
    return extractions

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", default=5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
