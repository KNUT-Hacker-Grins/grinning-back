import requests
from PIL import Image
from io import BytesIO

def download_image(image_url):
    response = requests.get(image_url, timeout=5)
    response.raise_for_status()
    return Image.open(BytesIO(response.content)).convert('RGB')