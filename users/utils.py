from logging import getLogger

import requests
from django.core.files.uploadedfile import UploadedFile

from AskAnywhere import settings

log = getLogger(__name__)


def upload_image_to_imgbb(img_file: UploadedFile) -> str:
    link = f'https://api.imgbb.com/1/upload?key={settings.IMGBB_API_KEY}'
    files = {
        'image': (img_file.name, img_file.read(), img_file.content_type)
    }
    resp = requests.post(link, files=files, timeout=settings.IMGBB_TIMEOUT_SECONDS)
    log.debug(f'IMGBB request: {files}')
    log.debug(f'IMGBB response: {resp.json()}')
    return resp.json()['data']['url']
