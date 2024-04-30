import json
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

def download_image(image_url, save_path):
    headers = {
        'Referer': 'https://alisports.x.yupoo.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
    }
    response = requests.get(image_url, headers=headers)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)

def extract_product_details(url, driver):
    driver.get(url)
    time.sleep(3)  # Espera para a página carregar

    product_name = driver.find_element(By.CSS_SELECTOR, "span.showalbumheader__gallerytitle").text
    try:
        product_size = driver.find_element(By.CSS_SELECTOR, "span.showalbumheader__gallerytitle + span").text
    except:
        product_size = "Tamanho não disponível"

    product_folder = f"{product_name.replace(' ', '_')}_{product_size}"
    os.makedirs(product_folder, exist_ok=True)  # Cria uma pasta para as imagens do produto

    photos = driver.find_elements(By.CSS_SELECTOR, "div.showalbum__children.image__main")
    photo_details = []
    for photo in photos:
        img_element = photo.find_element(By.CSS_SELECTOR, "img")
        img_url = img_element.get_attribute('data-origin-src')
        if not img_url:
            img_url = img_element.get_attribute('src')  # backup caso data-origin-src esteja vazio
        img_url = "https:" + img_url if img_url.startswith("//") else img_url
        photo_title = photo.find_element(By.CSS_SELECTOR, "h3").get_attribute('title')
        file_path = os.path.join(product_folder, f"{photo_title.replace(' ', '_').replace(':', '_')}.jpg")

        download_image(img_url, file_path)
        photo_details.append({'title': photo_title, 'image_url': img_url, 'file_path': file_path})

    return {'product_name': product_name, 'size': product_size, 'photos': photo_details}

# Configuração do WebDriver
chrome_options = Options()
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(options=chrome_options)

try:
    driver.get("https://alisports.x.yupoo.com/categories/3846309")
    time.sleep(3)  # Espera a página carregar inicialmente

    product_blocks = driver.find_elements(By.CSS_SELECTOR, "div.categories__parent div.categories__children")
    products_info = []
    for block in product_blocks[:3]:  # Limitando a coleta aos três primeiros produtos
        link = block.find_element(By.CSS_SELECTOR, "a.album__main").get_attribute('href')
        products_info.append(link)

    all_product_details = []
    for link in products_info:
        details = extract_product_details(link, driver)
        all_product_details.append(details)

    with open('product_details.json', 'w', encoding='utf-8') as f:
        json.dump(all_product_details, f, ensure_ascii=False, indent=4)

    print("Dados salvos em 'product_details.json'.")

finally:
    driver.quit()  # Fecha o navegador
