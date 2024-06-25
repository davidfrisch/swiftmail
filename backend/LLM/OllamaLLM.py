from LLM.BaseLLM import BaseLLM
import requests
import json

class OllamaAI(BaseLLM):
  def __init__(self, ollama_api_url, model):
    super().__init__()
    self.ollama_api_url = ollama_api_url
    self.session = requests.Session()
    self.model = model
    self.health_check()
    
  def health_check(self):
    print(f'Performing health check on {self.ollama_api_url}')
    r = self.session.get(f'{self.ollama_api_url}')
    if r.status_code != 200:
        print(f'Health check failed: {r.text}')
        exit(1)

    print(r.text)
    print('Health check passed')
    

  def predict(self, prompt, format=None):
    r = self.session.post(f'{self.ollama_api_url}/api/generate',
                                json={
                                    'model': self.model,
                                    'prompt': prompt,
                                    'format': format
                                },
                                stream=True,
                            )
    r.raise_for_status()

    model_response = ""
    for line in r.iter_lines():
        body = json.loads(line)
        response_part = body.get('response', '')
        model_response += response_part

        if 'error' in body:
            raise Exception(body['error'])

        if body.get('done', False):
            return model_response
    
    