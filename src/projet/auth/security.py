from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, TYPE_CHECKING
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
import os
import secrets
import hashlib
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

if TYPE_CHECKING:
    from . import models

ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Import des settings centralisés
from projet.settings import settings

def _read_file(p: str) -> str:
    return Path(p).read_text(encoding="utf-8")

def _signing_key() -> str:
    if ALGORITHM == "HS256":
        secret_key = settings.SECRET_KEY
        if hasattr(secret_key, 'get_secret_value'):
            secret_key = secret_key.get_secret_value()
        if not secret_key or len(secret_key) < 32:
            raise RuntimeError("SECRET_KEY manquant ou trop court (>=32 chars) pour HS256")
        return secret_key
    # RS256 / ES256
    if not settings.PRIVATE_KEY_PATH or not Path(settings.PRIVATE_KEY_PATH).exists():
        raise RuntimeError("PRIVATE_KEY_PATH introuvable pour clés asymétriques")
    return _read_file(settings.PRIVATE_KEY_PATH)

def _verifying_key() -> str:
    if ALGORITHM == "HS256":
        return _signing_key()
    if not settings.PUBLIC_KEY_PATH or not Path(settings.PUBLIC_KEY_PATH).exists():
        raise RuntimeError("PUBLIC_KEY_PATH introuvable pour clés asymétriques")
    return _read_file(settings.PUBLIC_KEY_PATH)

def hash_password(p: str) -> str:
    return pwd_context.hash(p)

def verify_password(p: str, hp: str) -> bool:
    return pwd_context.verify(p, hp)

def create_access_token(subject: str, roles: Optional[list[str]] = None) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "roles": roles or [], "iat": int(now.timestamp()), "exp": int(exp.timestamp()), "type": "access"}
    return jwt.encode(payload, _signing_key(), algorithm=ALGORITHM)

def create_refresh_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(days=7)  # Refresh token valide 7 jours
    payload = {"sub": subject, "iat": int(now.timestamp()), "exp": int(exp.timestamp()), "type": "refresh"}
    return jwt.encode(payload, _signing_key(), algorithm=ALGORITHM)

def create_email_verification_token(email: str) -> str:
    """Crée un token pour la vérification d'email (valide 24h)"""
    now = datetime.now(timezone.utc)
    exp = now + timedelta(hours=24)
    payload = {"email": email, "iat": int(now.timestamp()), "exp": int(exp.timestamp()), "type": "email_verification"}
    return jwt.encode(payload, _signing_key(), algorithm=ALGORITHM)

def create_password_reset_token(email: str) -> str:
    """Crée un token pour le reset de mot de passe (valide 1h)"""
    now = datetime.now(timezone.utc)
    exp = now + timedelta(hours=1)
    payload = {"email": email, "iat": int(now.timestamp()), "exp": int(exp.timestamp()), "type": "password_reset"}
    return jwt.encode(payload, _signing_key(), algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, _verifying_key(), algorithms=[ALGORITHM])

def hash_refresh_token(token: str) -> str:
    """Hash un refresh token pour le stockage sécurisé"""
    return hashlib.sha256(token.encode()).hexdigest()

def generate_secure_token(length: int = 32) -> str:
    """Génère un token sécurisé aléatoire"""
    return secrets.token_urlsafe(length)

def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="auth/login"))) -> "models.User":
    """Récupère l'utilisateur actuel depuis le token JWT"""
    from . import models, database
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    
    # Récupérer l'utilisateur depuis la DB
    db = database.SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.id == int(user_id)).first()
        if user is None:
            raise credentials_exception
        return user
    finally:
        db.close()