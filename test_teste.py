import logging
import os
from unittest.mock import MagicMock, mock_open, patch

import pytest
import requests
from watchdog.events import FileCreatedEvent

import arquivo
import monitoramento


@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setattr(arquivo, "WEBHOOK_URL", "http://test.url")


def test_disparar_automacao_success(mock_env, caplog):
    caplog.set_level(logging.INFO)
    with patch("arquivo.get_session") as mock_session, \
            patch("arquivo.datetime") as mock_datetime:
        mock_now = MagicMock()
        mock_now.strftime.return_value = "2024-01-01"
        mock_datetime.now.return_value = mock_now

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post = MagicMock()
        mock_post.post.return_value = mock_response
        mock_session.return_value = mock_post

        arquivo.disparar_automacao("http://img.url", "Test")

        mock_post.post.assert_called_once()

        args, kwargs = mock_post.post.call_args
        assert kwargs["json"]["caption"] == "Test - Gerado em: 2024-01-01"
        assert kwargs["timeout"] == 10
        assert "Status: 200" in caplog.text


def test_disparar_automacao_missing_env(monkeypatch, caplog):
    monkeypatch.setattr(arquivo, "WEBHOOK_URL", None)

    with patch("arquivo.get_session") as mock_session:
        arquivo.disparar_automacao("http://img.url", "Test")

        mock_session.assert_not_called()
        assert "A variável de ambiente" in caplog.text


def test_disparar_automacao_failure(mock_env, caplog):
    with patch("arquivo.get_session") as mock_session:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"
        
        mock_post = MagicMock()
        mock_post.post.return_value = mock_response
        mock_session.return_value = mock_post

        arquivo.disparar_automacao("http://img.url", "Test")

        assert "Status: 500" in caplog.text
        assert "Resposta: Server Error" in caplog.text


def test_disparar_automacao_exception(mock_env, caplog):
    with patch("arquivo.get_session") as mock_session:
        mock_post = MagicMock()
        mock_post.post.side_effect = requests.exceptions.RequestException("Connection Error")
        mock_session.return_value = mock_post

        arquivo.disparar_automacao("http://img.url", "Test")

        assert "Erro de conexão" in caplog.text


def test_upload_arquivo_drive_success(mock_env, caplog):
    caplog.set_level(logging.INFO)
    with patch("arquivo.get_session") as mock_session, \
            patch("builtins.open", mock_open(read_data=b"dados")):
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        mock_post = MagicMock()
        mock_post.post.return_value = mock_response
        mock_session.return_value = mock_post

        arquivo.upload_arquivo_drive("arquivo.txt")

        mock_post.post.assert_called_once()
        assert "files" in mock_post.post.call_args[1]
        assert "Upload concluído: 200" in caplog.text


def test_upload_arquivo_drive_with_schedule(mock_env, caplog):
    with patch("arquivo.get_session") as mock_session, \
            patch("builtins.open", mock_open(read_data=b"dados")):
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        mock_post = MagicMock()
        mock_post.post.return_value = mock_response
        mock_session.return_value = mock_post

        arquivo.upload_arquivo_drive("arquivo.txt", "2024-12-25 10:00", "Feliz Natal")

        mock_post.post.assert_called_once()
        kwargs = mock_post.post.call_args[1]
        assert kwargs["data"]["agendamento"] == "2024-12-25 10:00"
        assert kwargs["data"]["caption"] == "Feliz Natal"


def test_monitoramento_regex_agendamento(mock_env):
    handler = monitoramento.UploadHandler()

    with patch("monitoramento.arquivo.upload_arquivo_drive") as mock_upload, \
            patch("monitoramento.shutil.move") as mock_move, \
            patch("monitoramento.os.path.exists", return_value=True), \
            patch("monitoramento.time.sleep"):

        mock_upload.return_value = True

        nome_arquivo = "2025-01-01_12-00_Teste de Ano Novo.jpg"
        caminho_completo = os.path.join("pasta_monitorada", nome_arquivo)
        evento = FileCreatedEvent(caminho_completo)

        handler.on_created(evento)

        mock_upload.assert_called_once()
        args, _ = mock_upload.call_args
        assert args[0] == caminho_completo
        assert args[1] == "2025-01-01 12:00"
        assert args[2] == "Teste de Ano Novo"

        mock_move.assert_called_once()
        assert "Enviados" in mock_move.call_args[0][1]


def test_monitoramento_arquivo_comum(mock_env):
    handler = monitoramento.UploadHandler()

    with patch("monitoramento.arquivo.upload_arquivo_drive") as mock_upload, \
            patch("monitoramento.shutil.move") as mock_move, \
            patch("monitoramento.os.path.exists", return_value=True), \
            patch("monitoramento.time.sleep"):

        mock_upload.return_value = False

        evento = FileCreatedEvent(os.path.join("pasta_monitorada", "foto.png"))
        handler.on_created(evento)

        assert "Erros" in mock_move.call_args[0][1]


def test_caption_preservation_on_invalid_date(mock_env):
    handler = monitoramento.UploadHandler()

    with patch("monitoramento.arquivo.upload_arquivo_drive") as mock_upload, \
            patch("monitoramento.shutil.move") as mock_move, \
            patch("monitoramento.os.path.exists", return_value=True), \
            patch("monitoramento.time.sleep"):

        mock_upload.return_value = True

        # Arquivo com data inválida (mês 13)
        nome_arquivo = "2024-13-01_12-00_Minha Legenda.jpg"
        caminho_completo = os.path.join("pasta_monitorada", nome_arquivo)
        evento = FileCreatedEvent(caminho_completo)

        handler.on_created(evento)

        mock_upload.assert_called_once()
        args, _ = mock_upload.call_args
        # O agendamento deve ser None porque a data é inválida
        assert args[1] is None
        # A legenda DEVE ser preservada
        assert args[2] == "Minha Legenda"