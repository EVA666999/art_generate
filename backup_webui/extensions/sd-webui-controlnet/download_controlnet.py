import requests
import os

def download_file(url, filename):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    downloaded = 0
    
    print(f"Скачивание {filename}...")
    with open(filename, 'wb') as f:
        for data in response.iter_content(block_size):
            downloaded += len(data)
            f.write(data)
            done = int(50 * downloaded / total_size)
            print(f"\r[{'=' * done}{' ' * (50-done)}] {downloaded}/{total_size} байт", end='')
    print("\nСкачивание завершено!")

# URL модели
url = "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_face.pth"
filename = "models/control_v11p_sd15_face.pth"

# Создаем директорию если её нет
os.makedirs("models", exist_ok=True)

# Скачиваем файл
download_file(url, filename) 