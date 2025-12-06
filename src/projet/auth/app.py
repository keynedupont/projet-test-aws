from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
from .routers import auth as auth_router
from .database import Base, engine, get_db
from . import models, security
from projet.settings import settings
from projet.middleware import setup_error_middleware
import redis.asyncio as redis

# (les tables seront créées par migrations Alembic)
app = FastAPI(title="Auth Service")

# Middleware de gestion d'erreurs global
setup_error_middleware(app)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(",") if hasattr(settings, 'CORS_ORIGINS') else ["http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Rate limiting setup (optionnel)
@app.on_event("startup")
async def startup():
    try:
        redis_client = redis.from_url(settings.REDIS_URL if hasattr(settings, 'REDIS_URL') else "redis://localhost:6379")
        await FastAPILimiter.init(redis_client)
        print("✅ Rate limiting activé avec Redis")
    except Exception as e:
        print(f"⚠️ Rate limiting désactivé (Redis non disponible): {e}")

app.include_router(auth_router.router)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = security.decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    u = db.get(models.User, user_id)
    if not u or not u.is_active:
        raise HTTPException(401, "Inactive or not found")
    return u

@app.get("/me")
def me(user = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "is_verified": user.is_verified, "roles": [r.name for r in user.roles]}


@app.get("/health")
async def health():
    """Endpoint de santé: non-bloquant en dev; remonte l'état des dépendances."""
    status = {"status": "ok", "db": False, "redis": False}
    # Check DB
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
            status["db"] = True
    except Exception:
        status["db"] = False
    # Check Redis (optionnel)
    try:
        redis_client = redis.from_url(settings.REDIS_URL if hasattr(settings, 'REDIS_URL') else "redis://localhost:6379")
        await redis_client.ping()
        status["redis"] = True
    except Exception:
        status["redis"] = False
    # Toujours 200 pour éviter des boucles de restart en dev
    return JSONResponse(status, status_code=200)