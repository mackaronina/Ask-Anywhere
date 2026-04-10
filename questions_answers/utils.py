from logging import getLogger

import requests

from AskAnywhere import settings

log = getLogger(__name__)


def generate_ai_answer_text(question_title: str, question_text: str) -> str:
    link = f'https://api.cloudflare.com/client/v4/accounts/{settings.CLOUDFLARE_ACCOUNT_ID}/ai/run/{settings.CLOUDFLARE_MODEL_NAME}'
    headers = {
        'Authorization': f'Bearer {settings.CLOUDFLARE_API_KEY}'
    }
    data = {
        'messages': [
            {
                'role': 'system',
                'content': ('You are an experienced user of a site where people ask questions. Each question contains '
                            'a title and question text. Your task is to write short but correct answers to these '
                            'questions. Your responses should only contain the text of your response as a site user')
            },
            {
                'role': 'user',
                'content': f'Write an answer to the question with a title "{question_title}" and text "{question_text}"'
            }
        ]
    }
    response = requests.post(link, json=data, headers=headers, timeout=settings.CLOUDFLARE_TIMEOUT_SECONDS)
    log.debug(f'Cloudflare API request: {data}')
    log.debug(f'Cloudflare API response: {response.json()}')
    return response.json()['result']['response']
