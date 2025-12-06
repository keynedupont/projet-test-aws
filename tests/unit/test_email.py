"""Tests unitaires pour le module email"""

import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from projet.auth import email


def test_send_verification_email_console(caplog):
    """Test que l'email de vérification est loggé en mode console"""
    with patch('projet.auth.email.settings') as mock_settings:
        mock_settings.EMAIL_BACKEND = "console"
        mock_settings.BASE_URL = "http://localhost:8001"
        
        email.send_verification_email("test@example.com", "token123")
        
        # Vérifier que l'email a été loggé
        assert "test@example.com" in caplog.text
        assert "token123" in caplog.text
        assert "verify-email" in caplog.text


def test_send_reset_password_email_console(caplog):
    """Test que l'email de reset password est loggé en mode console"""
    with patch('projet.auth.email.settings') as mock_settings:
        mock_settings.EMAIL_BACKEND = "console"
        mock_settings.BASE_URL = "http://localhost:8001"
        
        email.send_reset_password_email("test@example.com", "token456")
        
        # Vérifier que l'email a été loggé
        assert "test@example.com" in caplog.text
        assert "token456" in caplog.text
        assert "reset-password" in caplog.text


def test_send_verification_email_file(tmp_path, monkeypatch):
    """Test que l'email de vérification est sauvegardé dans un fichier"""
    email_file = tmp_path / "test_emails.json"
    monkeypatch.setattr(email.settings, "EMAIL_BACKEND", "file")
    monkeypatch.setattr(email.settings, "BASE_URL", "http://localhost:8001")
    
    # Mock le chemin /tmp/emails.json
    with patch('projet.auth.email.Path', return_value=email_file):
        email.send_verification_email("test@example.com", "token123")
        
        # Vérifier que le fichier existe
        assert email_file.exists()
        
        # Lire et vérifier le contenu
        with open(email_file, "r", encoding="utf-8") as f:
            emails = json.load(f)
        
        assert len(emails) == 1
        assert emails[0]["to"] == "test@example.com"
        assert "token123" in emails[0]["html_body"]
        assert "token123" in emails[0]["text_body"]
        assert "verify-email" in emails[0]["html_body"]


def test_send_reset_password_email_file(tmp_path, monkeypatch):
    """Test que l'email de reset password est sauvegardé dans un fichier"""
    email_file = tmp_path / "test_emails.json"
    monkeypatch.setattr(email.settings, "EMAIL_BACKEND", "file")
    monkeypatch.setattr(email.settings, "BASE_URL", "http://localhost:8001")
    
    # Mock le chemin /tmp/emails.json
    with patch('projet.auth.email.Path', return_value=email_file):
        email.send_reset_password_email("test@example.com", "token456")
        
        # Vérifier que le fichier existe
        assert email_file.exists()
        
        # Lire et vérifier le contenu
        with open(email_file, "r", encoding="utf-8") as f:
            emails = json.load(f)
        
        assert len(emails) == 1
        assert emails[0]["to"] == "test@example.com"
        assert "token456" in emails[0]["html_body"]
        assert "token456" in emails[0]["text_body"]
        assert "reset-password" in emails[0]["html_body"]


@patch('projet.auth.email.smtplib.SMTP')
def test_send_verification_email_smtp(mock_smtp, monkeypatch):
    """Test que l'email de vérification est envoyé via SMTP (mocké)"""
    monkeypatch.setattr(email.settings, "EMAIL_BACKEND", "smtp")
    monkeypatch.setattr(email.settings, "BASE_URL", "http://localhost:8001")
    monkeypatch.setattr(email.settings, "SMTP_HOST", "smtp.example.com")
    monkeypatch.setattr(email.settings, "SMTP_PORT", 587)
    monkeypatch.setattr(email.settings, "SMTP_USER", "user@example.com")
    monkeypatch.setattr(email.settings, "SMTP_PASSWORD", "password123")
    monkeypatch.setattr(email.settings, "SMTP_TLS", True)
    
    # Mock du serveur SMTP
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server
    
    email.send_verification_email("test@example.com", "token123")
    
    # Vérifier que SMTP a été appelé
    mock_smtp.assert_called_once_with("smtp.example.com", 587)
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with("user@example.com", "password123")
    mock_server.send_message.assert_called_once()
    mock_server.quit.assert_called_once()


@patch('projet.auth.email.smtplib.SMTP')
def test_send_reset_password_email_smtp(mock_smtp, monkeypatch):
    """Test que l'email de reset password est envoyé via SMTP (mocké)"""
    monkeypatch.setattr(email.settings, "EMAIL_BACKEND", "smtp")
    monkeypatch.setattr(email.settings, "BASE_URL", "http://localhost:8001")
    monkeypatch.setattr(email.settings, "SMTP_HOST", "smtp.example.com")
    monkeypatch.setattr(email.settings, "SMTP_PORT", 587)
    monkeypatch.setattr(email.settings, "SMTP_USER", "user@example.com")
    monkeypatch.setattr(email.settings, "SMTP_PASSWORD", "password123")
    monkeypatch.setattr(email.settings, "SMTP_TLS", True)
    
    # Mock du serveur SMTP
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server
    
    email.send_reset_password_email("test@example.com", "token456")
    
    # Vérifier que SMTP a été appelé
    mock_smtp.assert_called_once_with("smtp.example.com", 587)
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with("user@example.com", "password123")
    mock_server.send_message.assert_called_once()
    mock_server.quit.assert_called_once()


def test_send_email_unknown_backend_falls_back_to_console(caplog, monkeypatch):
    """Test qu'un backend inconnu utilise console par défaut"""
    monkeypatch.setattr(email.settings, "EMAIL_BACKEND", "unknown_backend")
    monkeypatch.setattr(email.settings, "BASE_URL", "http://localhost:8001")
    
    email.send_verification_email("test@example.com", "token123")
    
    # Vérifier que l'email a été loggé (fallback console)
    assert "test@example.com" in caplog.text
    assert "token123" in caplog.text

