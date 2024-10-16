import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from gigachat import GigaChat


class AI:
    def __init__(self, token):
        self.token = token

    async def get_gigachat_response(self, query: str) -> str:
        session = requests.Session()
        retries = Retry(total=5,
                        backoff_factor=0.1,
                        status_forcelist=[500, 502, 503, 504],
                        allowed_methods=frozenset(['GET', 'POST']))
        url = f'https://api.sber.ai/dialog/v1/chat?access_token={self.token}'
        session.mount(url, HTTPAdapter(max_retries=retries))
        response = session.post(url, json={'text': query})
        return response.json()['text']

    async def answer_ai(self, query: str) -> str:
        with GigaChat(credentials=self.token, verify_ssl_certs=False) as giga:
            response = giga.chat(query)
            return response.choices[0].message.content
