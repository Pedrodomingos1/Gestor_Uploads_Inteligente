import requests


WEBHOOK_URL = "http://localhost:5678/webhook-test/postar-instagram"

payload = {
    "mensagem": "Saudações do motor de automação Python!",
    "autor": "Pedro Domingos",
    "data_missao": "2026-02-01"
}

try:
    response = requests.post(WEBHOOK_URL, json=payload)
    print(f"Status da Mensagem: {response.status_code}")
    print(f"Resposta do Castelo: {response.text}")
except Exception as e:
    print(f"Erro na travessia: {e}")