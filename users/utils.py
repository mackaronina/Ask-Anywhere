import requests
from django.core.files.uploadedfile import UploadedFile

from AskAnywhere import settings


def upload_image_to_imgbb(img_file: UploadedFile) -> str:
    link = f'https://api.imgbb.com/1/upload?key={settings.IMGBB_API_KEY}'
    files = {
        'image': (img_file.name, img_file.read(), img_file.content_type)
    }
    resp = requests.post(link, files=files, timeout=settings.IMGBB_TIMEOUT_SECONDS)
    return resp.json()['data']['url']
