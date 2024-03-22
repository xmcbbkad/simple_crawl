import requests
from retry import retry

class OpenaiApi():
    @retry(Exception, tries=3, delay=2)
    def call_openai_chat_api(self, messages, temperature=0.0, max_tokens=256):
        endpoint = "https://api.openai.com/v1/chat/completions"
        #endpoint = "https://openai.masterai.run/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer xxxx"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            #"model": "gpt-4",
            "messages": messages,
            "temperature": temperature,
            #"max_tokens": max_tokens
        }
        print(messages)
        response = requests.post(endpoint, headers=headers, json=payload)
        print(response)
        response_data = response.json()
        print(response_data)
        if "choices" in response_data and len(response_data["choices"]) > 0:
            generated_text = response_data["choices"][0]["message"]["content"]
            return generated_text
        else:
            #print(response_data)
            return "Error generating chat response"

