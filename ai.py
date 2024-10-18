from gigachat import GigaChat
from gradio_client import Client


class AI:
    def __init__(self, token):
        self.token = token
        self.client = Client("THUDM/CodeGeeX")

    async def answer_ai(self, query: str) -> str:
        with GigaChat(credentials=self.token, verify_ssl_certs=False) as giga:
            response = giga.chat(query)
            return response.choices[0].message.content

    async def talk_ai(self, query: str):
        query = self.client.predict(message=f"{query}", api_name="/chat")
        return query
