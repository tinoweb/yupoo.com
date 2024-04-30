import requests

def download_image(image_url, save_path):
    headers = {
        'Referer': 'https://alisports.x.yupoo.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
    }
    response = requests.get(image_url, headers=headers)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)

# Exemplo de uso
image_url = 'https://photo.yupoo.com/alisports/8b59e3a8/55d4d0a0.jpg'
download_image(image_url, 'local_image.jpg')