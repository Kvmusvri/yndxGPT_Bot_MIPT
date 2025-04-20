import os
import json
import time
import jwt
import requests
import asyncio
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

class YandexGPTManager:
    def __init__(self):
        self.model_uri = f"gpt://{os.getenv('YC_FOLDER_ID')}/yandexgpt-lite"
        self.api_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self.conversation_threads = {}  # {chat_id: [message1, message2, ...]}
        self.key_file = r"authorized_key.json"
        self.iam_token = self._generate_iam_token()
        self.max_history = 20  # максимум сообщений в истории

    def _generate_iam_token(self):
        try:
            with open(self.key_file, 'r') as f:
                key_data = json.load(f)

            private_key = serialization.load_pem_private_key(
                key_data['private_key'].encode(),
                password=None,
                backend=default_backend()
            )

            now = int(time.time())
            payload = {
                'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
                'iss': key_data['service_account_id'],
                'iat': now,
                'exp': now + 3600
            }
            headers = {'kid': key_data['id']}
            jwt_token = jwt.encode(
                payload,
                private_key,
                algorithm='PS256',
                headers=headers
            )

            response = requests.post(
                'https://iam.api.cloud.yandex.net/iam/v1/tokens',
                json={'jwt': jwt_token}
            )

            if response.status_code == 200:
                return response.json().get('iamToken')
            else:
                raise Exception(f"Ошибка генерации IAM-токена: {response.status_code} - {response.text}")

        except Exception as e:
            raise Exception(f"Не удалось сгенерировать IAM-токен: {str(e)}")

    def get_thread(self, chat_id):
        if chat_id not in self.conversation_threads:
            self.conversation_threads[chat_id] = [
                {"role": "system", "text": "Ты крутой ковбой повидавший многое и знающий много интересных фактов."}
            ]
        return self.conversation_threads[chat_id]

    def _trim_thread(self, thread):
        """Обрезает историю до последних N сообщений (max_history)."""
        if len(thread) > self.max_history:
            # Оставляем system + последние N-1 сообщений
            thread[:] = [thread[0]] + thread[-(self.max_history - 1):]

    async def send_message(self, chat_id, user_message):
        thread = self.get_thread(chat_id)
        thread.append({"role": "user", "text": user_message})
        self._trim_thread(thread)

        payload = {
            "modelUri": self.model_uri,
            "completionOptions": {
                "stream": False,
                "temperature": 0.9,
                "maxTokens": 1000
            },
            "messages": thread
        }

        headers = {
            "Authorization": f"Bearer {self.iam_token}",
            "Content-Type": "application/json"
        }

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(self.api_url, headers=headers, json=payload)
            )

            if response.status_code == 200:
                result = response.json()
                assistant_message = result["result"]["alternatives"][0]["message"]["text"]
                thread.append({"role": "assistant", "text": assistant_message})
                self._trim_thread(thread)
                return assistant_message
            elif response.status_code == 401:
                self.iam_token = self._generate_iam_token()
                headers["Authorization"] = f"Bearer {self.iam_token}"
                response = await loop.run_in_executor(
                    None,
                    lambda: requests.post(self.api_url, headers=headers, json=payload)
                )
                if response.status_code == 200:
                    result = response.json()
                    assistant_message = result["result"]["alternatives"][0]["message"]["text"]
                    thread.append({"role": "assistant", "text": assistant_message})
                    self._trim_thread(thread)
                    return assistant_message
                else:
                    return f"Ошибка API после обновления токена: {response.status_code} - {response.text}"
            else:
                return f"Ошибка API: {response.status_code} - {response.text}"

        except Exception as e:
            return f"Ошибка: {str(e)}"
