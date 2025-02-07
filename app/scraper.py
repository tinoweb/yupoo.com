import json
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from datetime import datetime
from . import models
from sqlalchemy.orm import Session

def download_image(image_url, save_path):
    headers = {
        'Referer': 'https://alisports.x.yupoo.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
    }
    response = requests.get(image_url, headers=headers)
    if response.status_code == 200:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            f.write(response.content)

def safe_find_element(driver, by, value, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except (TimeoutException, NoSuchElementException):
        return None

def safe_find_elements(driver, by, value, timeout=10):
    try:
        elements = WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((by, value))
        )
        return elements
    except (TimeoutException, NoSuchElementException):
        return []

def process_album(driver, album_url, folder_path):
    """
    Processa um álbum individual e extrai todas as suas imagens
    """
    try:
        driver.get(album_url)
        time.sleep(3)  # Aguarda o carregamento da página

        # Encontra todas as imagens do álbum
        images = safe_find_elements(driver, By.CSS_SELECTOR, "div.showalbum__children.image__main img")
        
        if not images:
            raise Exception("Nenhuma imagem encontrada no álbum")

        image_details = []
        for idx, img in enumerate(images, 1):
            try:
                # Tenta obter a URL da imagem em alta resolução
                img_url = img.get_attribute('data-origin-src')
                if not img_url:
                    img_url = img.get_attribute('data-src')
                if not img_url:
                    img_url = img.get_attribute('src')

                if not img_url:
                    print(f"URL não encontrada para imagem {idx}, pulando...")
                    continue

                img_url = "https:" + img_url if img_url.startswith("//") else img_url
                
                # Nome do arquivo baseado no título original ou índice
                original_name = img.get_attribute('alt') or f"imagem_{idx:03d}"
                file_name = f"{original_name}.jpg"
                file_path = os.path.join(folder_path, file_name)

                print(f"Baixando imagem {idx}: {img_url}")
                download_image(img_url, file_path)

                image_details.append({
                    'index': idx,
                    'original_name': original_name,
                    'image_url': img_url,
                    'file_path': file_path
                })

            except Exception as e:
                print(f"Erro ao processar imagem {idx} do álbum: {str(e)}")

        return image_details

    except Exception as e:
        print(f"Erro ao processar álbum {album_url}: {str(e)}")
        return []

def collect_album_info(driver):
    """
    Coleta informações de todos os álbuns da página atual
    """
    albums_info = []
    albums = safe_find_elements(driver, By.CSS_SELECTOR, "div.categories__children")
    
    if not albums:
        raise Exception("Nenhum álbum encontrado na página")

    print(f"Encontrados {len(albums)} álbuns")

    for idx, album in enumerate(albums, 1):
        try:
            title_element = safe_find_element(album, By.CSS_SELECTOR, "div.text_overflow.album__title")
            title = title_element.text if title_element else f"Album_{idx}"
            
            link_element = safe_find_element(album, By.CSS_SELECTOR, "a.album__main")
            album_url = link_element.get_attribute('href') if link_element else None

            if album_url:
                albums_info.append({
                    'title': title,
                    'url': album_url,
                    'index': idx
                })
            else:
                print(f"Link não encontrado para álbum {title}, pulando...")

        except Exception as e:
            print(f"Erro ao coletar informações do álbum {idx}: {str(e)}")
    
    return albums_info

def process_extraction(extraction: models.Extraction, db: Session):
    print(f"Iniciando extração da URL: {extraction.url}")
    try:
        # Atualiza status para processando
        extraction.status = "processing"
        db.commit()

        # Configura o Chrome em modo headless
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        # Inicializa o driver
        driver = webdriver.Chrome(options=chrome_options)
        print("Driver do Chrome inicializado")

        try:
            # Cria pasta para os resultados
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_folder = os.path.join("extractions", f"extraction_{extraction.id}_{timestamp}")
            os.makedirs(result_folder, exist_ok=True)
            print(f"Pasta de resultados criada: {result_folder}")

            # Carrega a página principal e coleta informações dos álbuns
            driver.get(extraction.url)
            time.sleep(5)
            print("Página carregada, coletando informações dos álbuns...")

            # Coleta informações de todos os álbuns primeiro
            albums_info = collect_album_info(driver)

            if not albums_info:
                raise Exception("Nenhum álbum encontrado para processar")

            albums_details = []
            # Processa cada álbum usando as informações coletadas
            for album in albums_info:
                try:
                    # Cria pasta para o álbum
                    safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in album['title'])
                    album_folder = os.path.join(result_folder, safe_title)
                    os.makedirs(album_folder, exist_ok=True)

                    print(f"\nProcessando álbum {album['index']}/{len(albums_info)}: {album['title']}")
                    
                    # Processa o álbum e obtém detalhes das imagens
                    images = process_album(driver, album['url'], album_folder)

                    if images:
                        albums_details.append({
                            'title': album['title'],
                            'url': album['url'],
                            'folder': album_folder,
                            'images': images
                        })
                    else:
                        print(f"Nenhuma imagem encontrada no álbum: {album['title']}")

                except Exception as e:
                    print(f"Erro ao processar álbum {album['index']}: {str(e)}")
                    continue

            if not albums_details:
                raise Exception("Nenhum álbum foi processado com sucesso")

            # Salva os detalhes em JSON
            details = {
                'url': extraction.url,
                'albums': albums_details,
                'total_albums': len(albums_details),
                'extraction_date': datetime.now().isoformat()
            }
            
            json_path = os.path.join(result_folder, "details.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(details, f, ensure_ascii=False, indent=4)

            print(f"Extração concluída com sucesso: {len(albums_details)} álbuns processados")

            # Atualiza o status da extração
            extraction.status = "completed"
            extraction.result_path = result_folder
            extraction.completed_at = datetime.now()
            db.commit()

        finally:
            driver.quit()
            print("Driver do Chrome fechado")

    except Exception as e:
        print(f"Erro durante a extração: {str(e)}")
        extraction.status = "failed"
        extraction.result_path = str(e)
        db.commit()
        raise
