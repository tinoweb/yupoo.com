from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

chrome_options = Options()
# Suas opções do Chrome

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)

url = "https://www.tramontina.com.br/departamentos/utilidades-domesticas/eletroportateis/"
driver.get(url)

print("Acessando a URL:", url)
time.sleep(3)  # Ou utilize espera explícita para elementos específicos

links_produtos = []

# Coletando os links dos produtos
print("Coletando os links dos produtos...")
produtos = driver.find_elements(By.CSS_SELECTOR, '.tr-gridTile')
for produto in produtos:
    link = produto.find_element(By.TAG_NAME, 'a').get_attribute('href')
    links_produtos.append(link)

print(f"Total de produtos encontrados: {len(links_produtos)}")

dados_produtos = []

# Iterando sobre cada produto para coletar mais detalhes
for index, link_produto in enumerate(links_produtos, start=1):
    print(f"Acessando detalhes do produto {index}/{len(links_produtos)}: {link_produto}")
    driver.get(link_produto)
    
    dados_produto = {}
    
    dados_produto['link'] = link_produto
    nome = driver.find_element(By.CLASS_NAME, 'productInfo__name').text.strip()
    print(f"Nome do Produto: {nome}")
    dados_produto['nome'] = nome
    
    valor = driver.find_element(By.CLASS_NAME, 'tr-productPrice__price').text.strip()
    print(f"Valor: {valor}")
    dados_produto['valor'] = valor
    
    # Descrição
    print("Coletando descrição...")
    descricao = []
    elementos_descricao = driver.find_elements(By.CLASS_NAME, 'description__accordion')
    for elemento_descricao in elementos_descricao:
        descricao.append(elemento_descricao.text.strip())
    dados_produto['descricao'] = " ".join(descricao)
    
    # Imagens
    print("Coletando imagens...")
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'slick-list')))
    elementos_imagens = driver.find_elements(By.CSS_SELECTOR, '.slick-slide img')
    imagens = [elem.get_attribute('src') for elem in elementos_imagens]
    print(f"Total de imagens coletadas: {len(imagens)}")
    dados_produto['imagens'] = imagens
    
    dados_produtos.append(dados_produto)

driver.quit()

# Salvando os dados em um arquivo JSON
arquivo_json = 'dados_produtos.json'
with open(arquivo_json, 'w', encoding='utf-8') as f:
    json.dump(dados_produtos, f, ensure_ascii=False, indent=4)
print(f"Todos os dados foram salvos com sucesso em {arquivo_json}.")
