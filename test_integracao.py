import os
import shutil
import time
from unittest.mock import patch
from watchdog.events import FileCreatedEvent
import monitoramento
import pytest

@pytest.fixture
def ambiente_monitoramento():
    pasta_monitorada = "pasta_monitorada_teste"
    pasta_enviados = os.path.join(pasta_monitorada, "Enviados")
    pasta_erros = os.path.join(pasta_monitorada, "Erros")

    os.makedirs(pasta_monitorada, exist_ok=True)

    yield {
        "monitorada": pasta_monitorada,
        "enviados": pasta_enviados,
        "erros": pasta_erros
    }

    if os.path.exists(pasta_monitorada):
        shutil.rmtree(pasta_monitorada)

def test_fluxo_completo_sucesso(ambiente_monitoramento):
    pastas = ambiente_monitoramento

    # Mock do upload para retornar sucesso
    with patch("monitoramento.arquivo.upload_arquivo_drive", return_value=True) as mock_upload, \
            patch("monitoramento.time.sleep"): # Skip sleep

        handler = monitoramento.UploadHandler()

        nome_arquivo = "2024-01-01_10-00_TesteIntegracao.jpg"
        caminho_origem = os.path.join(pastas["monitorada"], nome_arquivo)

        # Criar arquivo (necessário para o move funcionar)
        with open(caminho_origem, "wb") as f:
            f.write(b"conteudo")

        evento = FileCreatedEvent(caminho_origem)
        handler.on_created(evento)

        # Verificar se upload foi chamado
        mock_upload.assert_called_once()
        args = mock_upload.call_args[0]
        assert args[0] == caminho_origem
        assert args[1] == "2024-01-01 10:00"
        assert args[2] == "TesteIntegracao"

        # Verificar se arquivo foi movido para Enviados
        caminho_destino = os.path.join(pastas["enviados"], nome_arquivo)
        assert os.path.exists(caminho_destino)
        assert not os.path.exists(caminho_origem)

def test_fluxo_completo_erro_upload(ambiente_monitoramento):
    pastas = ambiente_monitoramento

    # Mock do upload para retornar falha
    with patch("monitoramento.arquivo.upload_arquivo_drive", return_value=False) as mock_upload, \
            patch("monitoramento.time.sleep"):

        handler = monitoramento.UploadHandler()

        nome_arquivo = "foto_simples.png"
        caminho_origem = os.path.join(pastas["monitorada"], nome_arquivo)

        # Criar arquivo
        with open(caminho_origem, "wb") as f:
            f.write(b"conteudo")

        evento = FileCreatedEvent(caminho_origem)
        handler.on_created(evento)

        # Verificar se upload foi chamado
        mock_upload.assert_called_once()

        # Verificar se arquivo foi movido para Erros
        caminho_destino = os.path.join(pastas["erros"], nome_arquivo)
        assert os.path.exists(caminho_destino)
        assert not os.path.exists(caminho_origem)
