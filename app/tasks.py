from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import requests
from datetime import datetime
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models
from .celery_app import app as celery_app
import logging

# Configuração de logging
logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def configure_driver(headless=True):
    """Configura e retorna uma instância do WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    if headless:
        chrome_options.add_argument("--headless=new")
    
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    return driver

# def download_image(url, file_path):
#     """Baixa uma imagem e salva no caminho especificado."""
#     try:
#         response = requests.get(url, stream=True)
#         if response.status_code == 200:
#             with open(file_path, 'wb') as file:
#                 for chunk in response.iter_content(1024):
#                     file.write(chunk)
#             return True
#         else:
#             logger.warning(f"Erro ao baixar imagem: {url} - Status Code: {response.status_code}")
#             return False
#     except Exception as e:
#         logger.error(f"Erro ao baixar imagem {url}: {str(e)}")
#         return False

def download_image(image_url, save_path):
    """Baixa a imagem para o caminho especificado."""
    try:
        # Criar diretório pai se não existir
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
        }
        
        response = requests.get(image_url, headers=headers, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return True
        return False
    except Exception as e:
        logger.error(f"Erro ao baixar imagem: {str(e)}")
        return False

def extract_product_details(url, driver, base_dir):
    """Extrai os detalhes de um produto específico."""
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 20)

        product_name = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span.showalbumheader__gallerytitle"))
        ).text

        try:
            product_size = driver.find_element(By.CSS_SELECTOR, "span.showalbumheader__gallerytitle + span").text
        except:
            product_size = "Tamanho não disponível"

        # Cria uma pasta para as imagens do produto
        product_folder = os.path.join(
            base_dir,
            f"{product_name.replace(' ', '_').replace('/', '_')}_{product_size}"
        )
        os.makedirs(product_folder, exist_ok=True)

        # Espera explícita pelas imagens
        photos = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.showalbum__children.image__main"))
        )

        photo_details = []
        for photo in photos:
            try:
                img_element = photo.find_element(By.CSS_SELECTOR, "img")
                img_url = img_element.get_attribute('data-origin-src')
                if not img_url:
                    img_url = img_element.get_attribute('src')
                img_url = "https:" + img_url if img_url.startswith("//") else img_url
                
                photo_title = photo.find_element(By.CSS_SELECTOR, "h3").get_attribute('title')
                file_path = os.path.join(product_folder, f"{photo_title.replace(' ', '_').replace(':', '_').replace('/', '_')}.jpg")

                if not os.path.exists(file_path):  # Verifica se o arquivo já existe
                    if download_image(img_url, file_path):
                        photo_details.append({'title': photo_title, 'image_url': img_url, 'file_path': file_path})
                else:
                    logger.info(f"Arquivo já existe: {file_path}")
                    photo_details.append({'title': photo_title, 'image_url': img_url, 'file_path': file_path})

            except Exception as e:
                logger.error(f"Erro ao processar foto: {str(e)}")
                continue

        return {'product_name': product_name, 'size': product_size, 'photos': photo_details}
    
    except Exception as e:
        logger.error(f"Erro ao processar produto {url}: {str(e)}")
        return None

@celery_app.task(bind=True, max_retries=3, name='extract_yupoo_data')
def extract_yupoo_data(self, url: str, extraction_id: int):
    """
    Task para extrair dados do Yupoo em background com atualização de status.
    """
    db = SessionLocal()
    driver = None
    try:
        # Consultar o banco de dados para obter o objeto extraction
        extraction = db.query(models.Extraction).filter(models.Extraction.id == extraction_id).first()
        if not extraction:
            logger.error(f"Extraction {extraction_id} not found")
            return {"status": "error", "message": "Extração não encontrada"}

        # Gerar caminho da extração
        result_path = generate_result_path(extraction_id)
        os.makedirs(result_path, exist_ok=True)  # Criar diretório

        # Atualizar o banco com o caminho
        extraction.result_path = result_path
        extraction.status = "processing"
        extraction.started_at = datetime.utcnow()
        db.commit()

        # Atualizar status inicial
        self.update_state(state='PROCESSING', meta={'progress': 0})
        
        # Configurar driver
        driver = configure_driver()
        
        # Navegar para a URL
        driver.get(url)
        
        # Etapa 1: Coletar links dos produtos
        self.update_state(state='PROCESSING', meta={'progress': 10, 'stage': 'Coletando links'})
        
        product_blocks = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.categories__parent div.categories__children"))
        )
        
        products_info = []
        for block in product_blocks:
            try:
                link = block.find_element(By.CSS_SELECTOR, "a.album__main").get_attribute('href')
                products_info.append(link)
            except Exception as e:
                logger.warning(f"Erro ao obter link: {str(e)}")
                continue
        
        # Etapa 2: Processar cada produto
        total_products = len(products_info)
        all_product_details = []
        
        for index, link in enumerate(products_info):
            try:
                # Atualizar progresso
                progress = 10 + int((index + 1) / total_products * 80)
                self.update_state(state='PROCESSING', meta={
                    'progress': progress,
                    'stage': f'Processando produto {index + 1}/{total_products}'
                })
                
                # Processar produto
                driver.get(link)
                product_details = extract_product_details(link, driver, result_path)  # Passar result_path
                if product_details:
                    all_product_details.append(product_details)
                    
            except Exception as e:
                logger.error(f"Erro processando {link}: {str(e)}")
                continue
        
        # Etapa 3: Finalização
        extraction.status = "completed"
        extraction.completed_at = datetime.utcnow()
        db.commit()
        
        return {
            "status": "success",
            "message": "Extração concluída",
            "products_processed": len(all_product_details)
        }
        
    except Exception as e:
        logger.error(f"Erro na extração: {str(e)}")
        if 'extraction' in locals():  # Verifica se extraction foi definido
            extraction.status = "failed"
            extraction.error_message = str(e)
            db.commit()
        self.retry(exc=e, countdown=60 * 5)  # Retry após 5 minutos
        
    finally:
        if driver:
            driver.quit()
        db.close()

def generate_result_path(extraction_id):
    # """Gera o caminho para salvar os resultados da extração."""
    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # return f"extractions/extraction_{extraction_id}_{timestamp}"

    """Gera o caminho para salvar os resultados da extração."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = os.path.abspath("extractions")  # Caminho absoluto
    extraction_dir = os.path.join(base_dir, f"extraction_{extraction_id}_{timestamp}")
    
    # Cria o diretório principal se não existir
    os.makedirs(base_dir, exist_ok=True)
    return extraction_dir