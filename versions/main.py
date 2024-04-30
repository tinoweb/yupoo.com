import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# Configuração inicial do Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Roda em modo headless, sem abrir a janela do navegador
driver = webdriver.Chrome(options=chrome_options)

def extract_product_details(url):
    driver.get(url)
    time.sleep(3)  # Espera para a página carregar

    # Extrai o nome do produto
    product_name = driver.find_element(By.CSS_SELECTOR, "span.showalbumheader__gallerytitle").text
    # Tentativa de extrair o tamanho do produto
    try:
        product_size = driver.find_element(By.CSS_SELECTOR, "span.showalbumheader__gallerytitle + span").text
    except:
        product_size = "Tamanho não disponível"  # Pode ajustar conforme o necessário

    # Extrai todas as variações de fotos
    photos = driver.find_elements(By.CSS_SELECTOR, "div.showalbum__children.image__main")
    photo_details = []
    for photo in photos:
        img_url = photo.find_element(By.CSS_SELECTOR, "img").get_attribute('data-origin-src')
        photo_title = photo.find_element(By.CSS_SELECTOR, "h3").get_attribute('title')
        photo_details.append({'title': photo_title, 'image_url': img_url})

    return {'product_name': product_name, 'size': product_size, 'photos': photo_details}

try:
    driver.get("https://alisports.x.yupoo.com/categories/3846309")
    time.sleep(5)  # Espera para que a página carregue completamente

    # Encontrar todos os blocos de camisetas dentro do contêiner especificado
    product_blocks = driver.find_elements(By.CSS_SELECTOR, "div.categories__parent div.categories__children")
    products_info = []
    for block in product_blocks[:10]:  # Limitar a coleta aos três primeiros produtos
        link = block.find_element(By.CSS_SELECTOR, "a.album__main").get_attribute('href')
        products_info.append(link)

    # Visitar cada link de produto e extrair detalhes
    all_product_details = []
    for link in products_info:
        details = extract_product_details(link)
        all_product_details.append(details)

    # Salvar os dados extraídos em um arquivo JSON
    with open('product_details.json', 'w', encoding='utf-8') as f:
        json.dump(all_product_details, f, ensure_ascii=False, indent=4)

    print("Dados salvos em 'product_details.json'.")

finally:
    driver.quit()  # Fecha o navegador e termina o processo
