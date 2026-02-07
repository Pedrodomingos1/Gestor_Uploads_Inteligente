import logging
import os
from datetime import datetime
from typing import Optional

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

def get_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def disparar_automacao(image_url: str, caption: str) -> None:
    if not WEBHOOK_URL:
        logger.error("A variável de ambiente 'N8N_WEBHOOK_URL' não está definida.")
        return

    data_hoje = datetime.now().strftime("%Y-%m-%d")
    payload = {
        "image_url": image_url,
        "caption": f"{caption} - Gerado em: {data_hoje}",
        "folder_name": f"Postagens_{data_hoje}"
    }

    try:
        session = get_session()
        response = session.post(WEBHOOK_URL, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info(f"Status: {response.status_code}")
        else:
            logger.warning(f"Status: {response.status_code} - Resposta: {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de conexão: {e}")
    except Exception as e:
        logger.error(f"Erro: {e}")


def upload_arquivo_drive(caminho_arquivo: str, agendamento: Optional[str] = None, caption: Optional[str] = None) -> bool:
    if not WEBHOOK_URL:
        logger.error("A variável de ambiente 'N8N_WEBHOOK_URL' não está definida.")
        return False

    try:
        with open(caminho_arquivo, "rb") as f:
            files = {"file": (os.path.basename(caminho_arquivo), f)}
            data = {}
            if agendamento:
                data["agendamento"] = agendamento
            if caption:
                data["caption"] = caption

            session = get_session()
            response = session.post(WEBHOOK_URL, files=files, data=data, timeout=30)

        if response.status_code == 200:
            logger.info(f"Upload concluído: {response.status_code}")
            return True
        else:
            logger.warning(f"Erro no upload: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de conexão: {e}")
        return False
    except Exception as e:
        logger.error(f"Erro: {e}")
        return False


if __name__ == "__main__":
    img = "https://images.unsplash.com/photo-1542831371-29b0f74f9713"
    texto = "Automação escalável com Python e n8n."
    disparar_automacao(img, texto)