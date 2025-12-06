"""Module d'envoi d'emails avec backends multiples (console, file, smtp)"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from projet.settings import settings

logger = logging.getLogger(__name__)


def _send_email_console(to: str, subject: str, html_body: str, text_body: str) -> None:
    """Backend console : affiche l'email dans les logs"""
    # Utiliser print() pour garantir la visibilité dans les logs Docker
    print("=" * 80)
    print(f"📧 EMAIL CONSOLE - To: {to}")
    print(f"Subject: {subject}")
    print("-" * 80)
    print("HTML Body:")
    print(html_body)
    print("-" * 80)
    print("Text Body:")
    print(text_body)
    print("=" * 80)
    # Aussi logger pour les logs structurés
    logger.info("=" * 80)
    logger.info(f"EMAIL CONSOLE - To: {to}")
    logger.info(f"Subject: {subject}")
    logger.info("-" * 80)
    logger.info("HTML Body:")
    logger.info(html_body)
    logger.info("-" * 80)
    logger.info("Text Body:")
    logger.info(text_body)
    logger.info("=" * 80)


def _send_email_file(to: str, subject: str, html_body: str, text_body: str) -> None:
    """Backend file : écrit l'email dans /tmp/emails.json"""
    email_file = Path("/tmp/emails.json")
    
    email_data = {
        "to": to,
        "subject": subject,
        "html_body": html_body,
        "text_body": text_body,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        # Créer le répertoire parent si nécessaire
        email_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Lire les emails existants ou créer une nouvelle liste
        if email_file.exists():
            try:
                with open(email_file, "r", encoding="utf-8") as f:
                    emails = json.load(f)
                    if not isinstance(emails, list):
                        emails = []
            except (json.JSONDecodeError, FileNotFoundError, IOError):
                emails = []
        else:
            emails = []
        
        # Ajouter le nouvel email
        emails.append(email_data)
        
        # Écrire dans le fichier
        with open(email_file, "w", encoding="utf-8") as f:
            json.dump(emails, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Email sauvegardé dans {email_file}")
    except Exception as e:
        logger.error(f"Erreur lors de l'écriture de l'email dans {email_file}: {e}", exc_info=True)
        raise


def _send_email_smtp(to: str, subject: str, html_body: str, text_body: str) -> None:
    """Backend SMTP : envoie l'email via SMTP"""
    if not all([settings.SMTP_HOST, settings.SMTP_PORT, settings.SMTP_USER]):
        raise ValueError("Configuration SMTP incomplète (SMTP_HOST, SMTP_PORT, SMTP_USER requis)")
    
    # Créer le message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_USER
    msg["To"] = to
    
    # Ajouter les parties texte et HTML
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))
    
    # Connexion SMTP
    try:
        if settings.SMTP_TLS:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        
        if settings.SMTP_PASSWORD:
            password = settings.SMTP_PASSWORD.get_secret_value() if hasattr(settings.SMTP_PASSWORD, 'get_secret_value') else settings.SMTP_PASSWORD
            server.login(settings.SMTP_USER, password)
        
        server.send_message(msg)
        server.quit()
        logger.info(f"Email envoyé via SMTP à {to}")
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi SMTP: {e}")
        raise


def _get_backend():
    """Retourne la fonction backend appropriée"""
    backend = settings.EMAIL_BACKEND.lower()
    
    if backend == "console":
        return _send_email_console
    elif backend == "file":
        return _send_email_file
    elif backend == "smtp":
        return _send_email_smtp
    else:
        logger.warning(f"Backend email inconnu '{backend}', utilisation de 'console' par défaut")
        return _send_email_console


def send_verification_email(email: str, token: str) -> None:
    """Envoie un email de vérification avec le token"""
    verification_url = f"{settings.BASE_URL}/verify-email?token={token}"
    
    subject = "Vérification de votre adresse email"
    
    html_body = f"""
    <html>
      <body>
        <h2>Vérification de votre adresse email</h2>
        <p>Bonjour,</p>
        <p>Merci de vous être inscrit. Pour vérifier votre adresse email, cliquez sur le lien ci-dessous :</p>
        <p><a href="{verification_url}">{verification_url}</a></p>
        <p>Ce lien est valide pendant 24 heures.</p>
        <p>Si vous n'avez pas créé de compte, vous pouvez ignorer cet email.</p>
        <p>Cordialement,<br>L'équipe</p>
      </body>
    </html>
    """
    
    text_body = f"""
    Vérification de votre adresse email
    
    Bonjour,
    
    Merci de vous être inscrit. Pour vérifier votre adresse email, cliquez sur le lien ci-dessous :
    
    {verification_url}
    
    Ce lien est valide pendant 24 heures.
    
    Si vous n'avez pas créé de compte, vous pouvez ignorer cet email.
    
    Cordialement,
    L'équipe
    """
    
    backend = _get_backend()
    backend(email, subject, html_body, text_body)


def send_reset_password_email(email: str, token: str) -> None:
    """Envoie un email de reset de mot de passe avec le token"""
    reset_url = f"{settings.BASE_URL}/reset-password?token={token}"
    
    subject = "Réinitialisation de votre mot de passe"
    
    html_body = f"""
    <html>
      <body>
        <h2>Réinitialisation de votre mot de passe</h2>
        <p>Bonjour,</p>
        <p>Vous avez demandé à réinitialiser votre mot de passe. Cliquez sur le lien ci-dessous :</p>
        <p><a href="{reset_url}">{reset_url}</a></p>
        <p>Ce lien est valide pendant 1 heure.</p>
        <p>Si vous n'avez pas demandé cette réinitialisation, vous pouvez ignorer cet email.</p>
        <p>Cordialement,<br>L'équipe</p>
      </body>
    </html>
    """
    
    text_body = f"""
    Réinitialisation de votre mot de passe
    
    Bonjour,
    
    Vous avez demandé à réinitialiser votre mot de passe. Cliquez sur le lien ci-dessous :
    
    {reset_url}
    
    Ce lien est valide pendant 1 heure.
    
    Si vous n'avez pas demandé cette réinitialisation, vous pouvez ignorer cet email.
    
    Cordialement,
    L'équipe
    """
    
    backend = _get_backend()
    backend(email, subject, html_body, text_body)

