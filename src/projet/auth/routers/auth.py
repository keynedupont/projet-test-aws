from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jwt.exceptions import InvalidTokenError
from .. import schemas, models, security
from ..database import get_db
from ...settings import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.UserOut, status_code=201)
async def register(
    user: schemas.UserCreate, 
    db: Session = Depends(get_db),
    request: Request = None
):
    # Rate limiting (désactivé temporairement)
    # if request:
    #     await FastAPILimiter.check(request, RateLimiter(times=5, seconds=300))  # 5 tentatives par 5 min
    
    if db.query(models.User).filter_by(email=user.email).first():
        raise HTTPException(400, "Email already registered")
    
    # Créer l'utilisateur avec token de vérification
    verification_token = security.create_email_verification_token(user.email)
    u = models.User(
        email=user.email, 
        hashed_password=security.hash_password(user.password),
        email_verification_token=verification_token,
        first_name=user.first_name,
        last_name=user.last_name
    )
    db.add(u); db.commit(); db.refresh(u)
    
    # Assigner rôle par défaut "user"
    role = db.query(models.Role).filter_by(name="user").first()
    if not role:
        role = models.Role(name="user")
        db.add(role); db.commit(); db.refresh(role)
    link = models.UserRole(user_id=u.id, role_id=role.id)
    db.add(link); db.commit()
    
    # TODO: Envoyer email de vérification
    print(f"Email de vérification pour {user.email}: {verification_token}")
    
    return u

@router.post("/login", response_model=schemas.Token)
async def login(
    form: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db),
    request: Request = None
):
    # Rate limiting (désactivé temporairement)
    # if request:
    #     await FastAPILimiter.check(request, RateLimiter(times=5, seconds=300))  # 5 tentatives par 5 min
    
    u = db.query(models.User).filter_by(email=form.username).first()  # OAuth2PasswordRequestForm utilise 'username' pour l'email
    
    # Debug: Log de la tentative de connexion
    print(f"🔐 Tentative de connexion pour: {form.username}")
    print(f"👤 Utilisateur trouvé: {u is not None}")
    
    # Vérifier si le compte est verrouillé
    if u and u.locked_until and u.locked_until > datetime.utcnow():
        raise HTTPException(status.HTTP_423_LOCKED, "Account temporarily locked")
    
    if not u or not security.verify_password(form.password, u.hashed_password):
        # Incrémenter les tentatives échouées
        if u:
            u.failed_login_attempts += 1
            if u.failed_login_attempts >= 5:
                u.locked_until = datetime.utcnow() + timedelta(minutes=30)
            db.commit()
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    
    # Reset des tentatives échouées et mise à jour du dernier login
    u.failed_login_attempts = 0
    u.locked_until = None
    u.last_login = datetime.utcnow()
    db.commit()
    
    roles = [r.name for r in u.roles]
    access_token = security.create_access_token(str(u.id), roles=roles)
    refresh_token = security.create_refresh_token(str(u.id))
    
    # Stocker le refresh token hashé
    refresh_token_hash = security.hash_refresh_token(refresh_token)
    refresh_token_obj = models.RefreshToken(
        token_hash=refresh_token_hash,
        user_id=u.id,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(refresh_token_obj)
    db.commit()
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/refresh", response_model=schemas.Token)
async def refresh_token(
    request: schemas.RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    try:
        payload = security.decode_token(request.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token type")
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
        
        # Vérifier que le refresh token existe et n'est pas révoqué
        token_hash = security.hash_refresh_token(request.refresh_token)
        refresh_token_obj = db.query(models.RefreshToken).filter_by(
            token_hash=token_hash, 
            is_revoked=False
        ).first()
        
        if not refresh_token_obj or refresh_token_obj.expires_at < datetime.utcnow():
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired refresh token")
        
        # Révoker l'ancien refresh token
        refresh_token_obj.is_revoked = True
        
        # Créer de nouveaux tokens
        u = db.query(models.User).filter_by(id=int(user_id)).first()
        if not u:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
        
        roles = [r.name for r in u.roles]
        new_access_token = security.create_access_token(str(u.id), roles=roles)
        new_refresh_token = security.create_refresh_token(str(u.id))
        
        # Stocker le nouveau refresh token
        new_refresh_token_hash = security.hash_refresh_token(new_refresh_token)
        new_refresh_token_obj = models.RefreshToken(
            token_hash=new_refresh_token_hash,
            user_id=u.id,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.add(new_refresh_token_obj)
        db.commit()
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

@router.post("/verify-email")
async def verify_email(
    request: schemas.EmailVerification,
    db: Session = Depends(get_db)
):
    try:
        payload = security.decode_token(request.token)
        if payload.get("type") != "email_verification":
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid token type")
        
        email = payload.get("email")
        user = db.query(models.User).filter_by(email=email).first()
        
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        
        user.is_verified = True
        user.email_verification_token = None
        db.commit()
        
        return {"message": "Email verified successfully"}
        
    except InvalidTokenError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired token")

@router.post("/request-password-reset")
async def request_password_reset(
    request: schemas.PasswordResetRequest,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter_by(email=request.email).first()
    if user:
        # Créer un token de reset
        reset_token = security.create_password_reset_token(request.email)
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        db.commit()
        
        # TODO: Envoyer email avec le token
        print(f"Token de reset pour {request.email}: {reset_token}")
    
    # Toujours retourner 200 pour éviter l'énumération d'emails
    return {"message": "If the email exists, a reset link has been sent"}

@router.post("/reset-password")
async def reset_password(
    request: schemas.PasswordReset,
    db: Session = Depends(get_db)
):
    try:
        payload = security.decode_token(request.token)
        if payload.get("type") != "password_reset":
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid token type")
        
        email = payload.get("email")
        user = db.query(models.User).filter_by(
            email=email,
            password_reset_token=request.token
        ).first()
        
        if not user or user.password_reset_expires < datetime.utcnow():
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired token")
        
        # Mettre à jour le mot de passe
        user.hashed_password = security.hash_password(request.new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        user.failed_login_attempts = 0
        user.locked_until = None
        
        # Révoker tous les refresh tokens
        db.query(models.RefreshToken).filter_by(user_id=user.id).update({"is_revoked": True})
        
        db.commit()
        
        return {"message": "Password reset successfully"}
        
    except InvalidTokenError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired token")

@router.get("/me", response_model=schemas.UserOut)
async def get_current_user(current_user: models.User = Depends(security.get_current_user)):
    return current_user

@router.put("/me", response_model=schemas.UserOut)
async def update_current_user(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    # Mettre à jour les champs fournis
    if user_update.first_name is not None:
        current_user.first_name = user_update.first_name
    if user_update.last_name is not None:
        current_user.last_name = user_update.last_name
    if user_update.avatar_url is not None:
        current_user.avatar_url = user_update.avatar_url
    if user_update.theme_preference is not None:
        current_user.theme_preference = user_update.theme_preference
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/change-password")
async def change_password(
    password_change: schemas.PasswordChange,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    # Vérifier le mot de passe actuel
    if not security.verify_password(password_change.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Mot de passe actuel incorrect")
    
    # Mettre à jour le mot de passe
    current_user.hashed_password = security.hash_password(password_change.new_password)
    db.commit()
    
    return {"message": "Mot de passe changé avec succès"}