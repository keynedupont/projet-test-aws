from __future__ import annotations

from fastapi import FastAPI, Request, Form, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from typing import Optional
import httpx
import os

from projet.settings import settings
from projet.middleware import setup_error_middleware


class CookieConfig(BaseModel):
    name: str = settings.COOKIE_NAME
    domain: Optional[str] = None
    secure: bool = settings.COOKIE_SECURE or settings.APP_ENV == "production"
    httponly: bool = True
    samesite: str = "strict" if settings.APP_ENV == "production" else settings.COOKIE_SAMESITE


AUTH_SERVICE_URL = settings.AUTH_SERVICE_URL
COOKIE = CookieConfig()
HTTP_TIMEOUT = 5.0
client = httpx.AsyncClient(timeout=HTTP_TIMEOUT)

app = FastAPI(title="Minimal Web App")

# Middleware de gestion d'erreurs global
setup_error_middleware(app)

base_dir = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))

static_dir = os.path.join(base_dir, "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


def get_token_from_cookie(request: Request) -> str | None:
    return request.cookies.get(COOKIE.name)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "project_name": "projet"})


@app.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request, "error": None, "project_name": "projet"})


@app.post("/signup")
async def signup(
    request: Request,
    email: EmailStr = Form(...), 
    password: str = Form(...),
    confirm_password: str = Form(alias="confirm-password"),
    terms: bool = Form(...)
):
    # Validation côté client
    if password != confirm_password:
        return templates.TemplateResponse("signup.html", {
            "request": request,
            "error": "Les mots de passe ne correspondent pas",
            "project_name": "Plateforme ML"
        })
    
    if not terms:
        return templates.TemplateResponse("signup.html", {
            "request": request,
            "error": "Vous devez accepter les conditions d'utilisation",
            "project_name": "Plateforme ML"
        })
    
    try:
        r = await client.post(f"{AUTH_SERVICE_URL}/auth/register", json={
            "email": email, 
            "password": password,
            "first_name": None,
            "last_name": None
        })
        if r.status_code >= 400:
            try:
                if r.headers.get("content-type", "").startswith("application/json"):
                    error_data = r.json()
                    if isinstance(error_data, list) and len(error_data) > 0:
                        # Format Pydantic validation error
                        error_detail = error_data[0].get("msg", "Erreur de validation")
                    else:
                        error_detail = error_data.get("detail", "Erreur lors de l'inscription")
                else:
                    error_detail = r.text
            except:
                error_detail = "Erreur lors de l'inscription"
            
            return templates.TemplateResponse("signup.html", {
                "request": request,
                "error": error_detail,
                "project_name": "Plateforme ML"
            })
    except httpx.HTTPError:
        return templates.TemplateResponse("signup.html", {
            "request": request,
            "error": "Service d'authentification indisponible",
            "project_name": "Plateforme ML"
        })
    return RedirectResponse(url="/login", status_code=303)


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None, "project_name": "projet"})


@app.post("/login")
async def login(request: Request, response: Response, email: EmailStr = Form(...), password: str = Form(...)):
    data = {"username": str(email), "password": password}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    try:
        r = await client.post(f"{AUTH_SERVICE_URL}/auth/login", data=data, headers=headers)
    except httpx.HTTPError:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Service auth indisponible", "project_name": "projet"})
    if r.status_code != 200:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Identifiants invalides", "project_name": "projet"})
    token = r.json().get("access_token")
    resp = RedirectResponse(url="/dashboard", status_code=303)
    resp.set_cookie(
        key=COOKIE.name,
        value=token,
        httponly=COOKIE.httponly,
        secure=COOKIE.secure,
        samesite=COOKIE.samesite,
        domain=COOKIE.domain,
        path="/",
    )
    return resp


@app.get("/logout")
def logout(request: Request):
    resp = RedirectResponse(url="/", status_code=303)
    resp.delete_cookie(COOKIE.name, path="/", domain=COOKIE.domain)
    return resp


@app.get("/health")
async def health():
    """Endpoint de santé: vérifie la reachabilité du service auth."""
    # Check Auth reachability (optionnel, sans faire échouer l'appli web)
    ok_auth = False
    try:
        r = await client.get(f"{AUTH_SERVICE_URL}/health")
        ok_auth = r.status_code == 200
    except Exception:
        ok_auth = False
    status = {"status": "ok", "auth": ok_auth}
    code = 200
    return JSONResponse(status, status_code=code)


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    try:
        r = await client.get(f"{AUTH_SERVICE_URL}/me", headers={"Authorization": f"Bearer {token}"})
    except httpx.HTTPError:
        return RedirectResponse(url="/login", status_code=303)
    if r.status_code != 200:
        return RedirectResponse(url="/login", status_code=303)
    user = r.json()
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})


async def require_roles(token: str | None, needed: list[str]) -> bool:
    if not token:
        return False
    try:
        r = await client.get(f"{AUTH_SERVICE_URL}/me", headers={"Authorization": f"Bearer {token}"})
        if r.status_code != 200:
            return False
        roles = r.json().get("roles", [])
        return all(role in roles for role in needed)
    except httpx.HTTPError:
        return False


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    if not await require_roles(token, ["admin"]):
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # Récupérer les infos utilisateur pour l'affichage
    try:
        r = await client.get(f"{AUTH_SERVICE_URL}/me", headers={"Authorization": f"Bearer {token}"})
        if r.status_code == 200:
            user = r.json()
            return templates.TemplateResponse("admin.html", {"request": request, "user": user})
        else:
            return RedirectResponse(url="/login", status_code=303)
    except httpx.HTTPError:
        return RedirectResponse(url="/login", status_code=303)


@app.get("/admin/users", response_class=HTMLResponse)
async def admin_users(request: Request):
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    if not await require_roles(token, ["admin"]):
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # TODO: Récupérer la liste des utilisateurs depuis l'API
    return templates.TemplateResponse("admin-users.html", {"request": request, "users": []})


@app.get("/admin/roles", response_class=HTMLResponse)
async def admin_roles(request: Request):
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    if not await require_roles(token, ["admin"]):
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # TODO: Récupérer la liste des rôles depuis l'API
    return templates.TemplateResponse("admin-roles.html", {"request": request, "roles": []})


@app.get("/admin/stats", response_class=HTMLResponse)
async def admin_stats(request: Request):
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    if not await require_roles(token, ["admin"]):
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # TODO: Récupérer les statistiques depuis l'API
    return templates.TemplateResponse("admin-stats.html", {"request": request, "stats": {}})


@app.get("/admin/logs", response_class=HTMLResponse)
async def admin_logs(request: Request):
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    if not await require_roles(token, ["admin"]):
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # TODO: Récupérer les logs depuis l'API
    return templates.TemplateResponse("admin-logs.html", {"request": request, "logs": []})


@app.get("/admin/settings", response_class=HTMLResponse)
async def admin_settings(request: Request):
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    if not await require_roles(token, ["admin"]):
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # TODO: Récupérer les paramètres système depuis l'API
    return templates.TemplateResponse("admin-settings.html", {"request": request, "settings": {}})


@app.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot-password.html", {"request": request, "error": None, "success": None})


@app.post("/forgot-password")
async def forgot_password(request: Request, email: EmailStr = Form(...)):
    try:
        r = await client.post(f"{AUTH_SERVICE_URL}/auth/request-password-reset", json={"email": email})
        if r.status_code == 200:
            return templates.TemplateResponse("forgot-password.html", {
                "request": request, 
                "error": None, 
                "success": "Si cette adresse email existe, un lien de réinitialisation a été envoyé."
            })
        else:
            return templates.TemplateResponse("forgot-password.html", {
                "request": request, 
                "error": "Erreur lors de l'envoi de l'email", 
                "success": None
            })
    except httpx.HTTPError:
        return templates.TemplateResponse("forgot-password.html", {
            "request": request, 
            "error": "Service auth indisponible", 
            "success": None
        })


@app.get("/reset-password", response_class=HTMLResponse)
def reset_password_page(request: Request, token: str = None):
    if not token:
        return RedirectResponse(url="/forgot-password", status_code=303)
    return templates.TemplateResponse("reset-password.html", {"request": request, "token": token, "error": None})


@app.post("/reset-password")
async def reset_password(request: Request, token: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)):
    if password != confirm_password:
        return templates.TemplateResponse("reset-password.html", {
            "request": request, 
            "token": token, 
            "error": "Les mots de passe ne correspondent pas"
        })
    
    try:
        r = await client.post(f"{AUTH_SERVICE_URL}/auth/reset-password", json={
            "token": token, 
            "new_password": password
        })
        if r.status_code == 200:
            return RedirectResponse(url="/login?reset=success", status_code=303)
        else:
            return templates.TemplateResponse("reset-password.html", {
                "request": request, 
                "token": token, 
                "error": "Token invalide ou expiré"
            })
    except httpx.HTTPError:
        return templates.TemplateResponse("reset-password.html", {
            "request": request, 
            "token": token, 
            "error": "Service auth indisponible"
        })


@app.get("/account", response_class=HTMLResponse)
async def account_page(request: Request):
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    
    # Récupérer les infos utilisateur
    try:
        r = await client.get(f"{AUTH_SERVICE_URL}/me", headers={"Authorization": f"Bearer {token}"})
        if r.status_code == 200:
            user = r.json()
            return templates.TemplateResponse("account.html", {"request": request, "user": user, "error": None, "success": None})
        else:
            return RedirectResponse(url="/login", status_code=303)
    except httpx.HTTPError:
        return RedirectResponse(url="/login", status_code=303)


@app.post("/account")
async def update_account(request: Request, first_name: str = Form(None), last_name: str = Form(None)):
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    
    # TODO: Implémenter la mise à jour du profil côté API
    # Pour l'instant, on simule un succès
    try:
        r = await client.get(f"{AUTH_SERVICE_URL}/me", headers={"Authorization": f"Bearer {token}"})
        if r.status_code == 200:
            user = r.json()
            return templates.TemplateResponse("account.html", {
                "request": request, 
                "user": user, 
                "error": None, 
                "success": "Profil mis à jour avec succès !"
            })
        else:
            return RedirectResponse(url="/login", status_code=303)
    except httpx.HTTPError:
        return templates.TemplateResponse("account.html", {
            "request": request, 
            "user": {"email": "user@example.com"}, 
            "error": "Erreur lors de la mise à jour", 
            "success": None
        })


@app.get("/change-password", response_class=HTMLResponse)
async def change_password_page(request: Request):
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    
    return templates.TemplateResponse("change-password.html", {"request": request, "error": None, "success": None})


@app.post("/change-password")
async def change_password(request: Request, current_password: str = Form(...), new_password: str = Form(...), confirm_password: str = Form(...)):
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    
    if new_password != confirm_password:
        return templates.TemplateResponse("change-password.html", {
            "request": request, 
            "error": "Les mots de passe ne correspondent pas", 
            "success": None
        })
    
    # TODO: Implémenter le changement de mot de passe côté API
    # Pour l'instant, on simule un succès
    return templates.TemplateResponse("change-password.html", {
        "request": request, 
        "error": None, 
        "success": "Mot de passe changé avec succès !"
    })


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    
    # Récupérer les infos utilisateur
    try:
        r = await client.get(f"{AUTH_SERVICE_URL}/me", headers={"Authorization": f"Bearer {token}"})
        if r.status_code == 200:
            user = r.json()
            return templates.TemplateResponse("settings.html", {"request": request, "user": user, "error": None, "success": None})
        else:
            return RedirectResponse(url="/login", status_code=303)
    except httpx.HTTPError:
        return RedirectResponse(url="/login", status_code=303)


@app.post("/settings")
async def update_settings(request: Request, theme: str = Form("auto"), language: str = Form("fr")):
    token = get_token_from_cookie(request)
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    
    # TODO: Implémenter la sauvegarde des paramètres côté API
    # Pour l'instant, on simule un succès
    try:
        r = await client.get(f"{AUTH_SERVICE_URL}/me", headers={"Authorization": f"Bearer {token}"})
        if r.status_code == 200:
            user = r.json()
            # Simuler la mise à jour
            user["theme_preference"] = theme
            return templates.TemplateResponse("settings.html", {
                "request": request, 
                "user": user, 
                "error": None, 
                "success": "Paramètres sauvegardés avec succès !"
            })
        else:
            return RedirectResponse(url="/login", status_code=303)
    except httpx.HTTPError:
        return templates.TemplateResponse("settings.html", {
            "request": request, 
            "user": {"email": "user@example.com", "theme_preference": theme}, 
            "error": "Erreur lors de la sauvegarde", 
            "success": None
        })


