import logging
import os
import re
import shutil
import time
from datetime import datetime

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

import arquivo

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class UploadHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith((".jpg", ".png", ".mp4")):
            logger.info(f"Novo arquivo detectado: {event.src_path}")
            time.sleep(2)

            filename = os.path.basename(event.src_path)
            match = re.match(r"(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})_(.*)\.(jpg|png|mp4)", filename, re.IGNORECASE)

            agendamento = None
            caption = None

            if match:
                data_part, hora_part, texto_part, _ = match.groups()
                temp_agendamento = f"{data_part} {hora_part.replace('-', ':')}"
                caption = texto_part
                try:
                    datetime.strptime(temp_agendamento, "%Y-%m-%d %H:%M")
                    agendamento = temp_agendamento
                except ValueError:
                    logger.warning(f"Data inválida ignorada (upload será imediato): {temp_agendamento}")

            sucesso = arquivo.upload_arquivo_drive(event.src_path, agendamento, caption)

            nome_pasta = "Enviados" if sucesso else "Erros"
            pasta_destino = os.path.join(os.path.dirname(event.src_path), nome_pasta)
            os.makedirs(pasta_destino, exist_ok=True)

            destino = os.path.join(pasta_destino, os.path.basename(event.src_path))
            shutil.move(event.src_path, destino)
            logger.info(f"Arquivo movido para: {destino}")


def iniciar_monitoramento(pasta: str) -> None:
    os.makedirs(pasta, exist_ok=True)

    observer = Observer()
    observer.schedule(UploadHandler(), pasta, recursive=False)
    observer.start()
    logger.info(f"Monitorando a pasta: {pasta}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    iniciar_monitoramento("pasta_monitorada")