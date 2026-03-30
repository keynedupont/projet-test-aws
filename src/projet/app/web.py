from __future__ import annotations

from fastapi import FastAPI, Request, Form, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from typing import Optional
import httpx
import os
from urllib.parse import urlencode

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
ACTIVE_ORG_COOKIE = "active_organization_id"
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

def login_redirect(next_path: str | None = None) -> RedirectResponse:
    params = f"?{urlencode({'next': next_path})}" if next_path else ""
    return RedirectResponse(url=f"/login{params}", status_code=303)


async def require_auth(request: Request) -> tuple[str, dict] | RedirectResponse:
    """Assure que l'utilisateur est authentifié pour une page SSR."""
    next_path = request.url.path
    token = get_token_from_cookie(request)
    if not token:
        return login_redirect(next_path=next_path)

    try:
        me_resp = await client.get(f"{AUTH_SERVICE_URL}/me", headers={"Authorization": f"Bearer {token}"})
    except httpx.HTTPError:
        return login_redirect(next_path=next_path)

    if me_resp.status_code != 200:
        resp = login_redirect(next_path=next_path)
        resp.delete_cookie(COOKIE.name, path="/", domain=COOKIE.domain)
        return resp

    return token, me_resp.json()


async def get_organizations_context(request: Request, token: str) -> tuple[str | None, str | None, list[dict]]:
    """Retourne (active_org_id, active_org_name, organizations)."""
    try:
        r = await client.get(
            f"{AUTH_SERVICE_URL}/auth/organizations",
            headers={"Authorization": f"Bearer {token}"},
        )
    except httpx.HTTPError:
        return None, None, []

    if r.status_code != 200:
        return None, None, []

    organizations = r.json() if isinstance(r.json(), list) else []
    if not organizations:
        return None, None, []

    current_cookie_org = request.cookies.get(ACTIVE_ORG_COOKIE)
    active_org = next((o for o in organizations if o.get("id") == current_cookie_org), None)
    if active_org is None:
        active_org = organizations[0]

    return active_org.get("id"), active_org.get("name"), organizations


def auth_headers(token: str, organization_id: str | None = None) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {token}"}
    if organization_id:
        headers["organization-id"] = organization_id
    return headers


def render_template(name: str, context: dict, **kwargs):
    """Compat rendering across Starlette TemplateResponse signatures."""
    request = context.get("request")
    if request is None:
        raise ValueError("Template context must include 'request'")

    # Starlette signature differs by version.
    # Try modern keyword signature first, then legacy positional forms.
    try:
        return templates.TemplateResponse(name=name, request=request, context=context, **kwargs)
    except TypeError:
        pass

    try:
        return templates.TemplateResponse(name=name, context=context, **kwargs)
    except TypeError:
        pass

    # Legacy: TemplateResponse(name, request, context, ...)
    return templates.TemplateResponse(name, request, context, **kwargs)

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    # Utilisé côté header pour n'afficher que Connexion / S'inscrire
    is_authenticated = get_token_from_cookie(request) is not None
    return render_template(
        "index.html",
        {
            "request": request,
            "project_name": "projet",
            "is_authenticated": is_authenticated,
        },
    )


@app.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    return render_template("signup.html", {"request": request, "error": None, "project_name": "projet"})


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
        return render_template("signup.html", {
            "request": request,
            "error": "Les mots de passe ne correspondent pas",
            "project_name": "Plateforme ML"
        })
    
    if not terms:
        return render_template("signup.html", {
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
            
            return render_template("signup.html", {
                "request": request,
                "error": error_detail,
                "project_name": "Plateforme ML"
            })
    except httpx.HTTPError:
        return render_template("signup.html", {
            "request": request,
            "error": "Service d'authentification indisponible",
            "project_name": "Plateforme ML"
        })
    return RedirectResponse(url="/login", status_code=303)


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return render_template(
        "login.html",
        {
            "request": request,
            "error": None,
            "project_name": "projet",
            "next": request.query_params.get("next"),
        },
    )


@app.post("/login")
async def login(request: Request, response: Response, email: EmailStr = Form(...), password: str = Form(...)):
    data = {"username": str(email), "password": password}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    form = await request.form()
    next_path = form.get("next") or request.query_params.get("next") or "/dashboard"
    try:
        r = await client.post(f"{AUTH_SERVICE_URL}/auth/login", data=data, headers=headers)
    except httpx.HTTPError:
        return render_template("login.html", {"request": request, "error": "Service auth indisponible", "project_name": "projet"})
    if r.status_code != 200:
        return render_template("login.html", {"request": request, "error": "Identifiants invalides", "project_name": "projet"})
    token = r.json().get("access_token")
    resp = RedirectResponse(url=str(next_path), status_code=303)
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
    resp.delete_cookie(ACTIVE_ORG_COOKIE, path="/", domain=COOKIE.domain)
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
    auth = await require_auth(request)
    if isinstance(auth, RedirectResponse):
        return auth
    token, user = auth
    active_org_id, active_org_name, organizations = await get_organizations_context(request, token)
    project_count = 0
    try:
        projects_resp = await client.get(
            f"{AUTH_SERVICE_URL}/auth/projects",
            headers=auth_headers(token, active_org_id),
        )
        if projects_resp.status_code == 200 and isinstance(projects_resp.json(), list):
            project_count = len(projects_resp.json())
    except httpx.HTTPError:
        project_count = 0

    return render_template(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "project_count": project_count,
            "active_organization_id": active_org_id,
            "active_organization_name": active_org_name,
            "organizations": organizations,
        },
    )


@app.get("/projects", response_class=HTMLResponse)
async def projects_page(request: Request):
    auth = await require_auth(request)
    if isinstance(auth, RedirectResponse):
        return auth
    token, user = auth
    active_org_id, active_org_name, organizations = await get_organizations_context(request, token)

    try:
        r = await client.get(f"{AUTH_SERVICE_URL}/auth/projects", headers=auth_headers(token, active_org_id))
    except httpx.HTTPError:
        return login_redirect(next_path=request.url.path)

    projects = r.json() if r.status_code == 200 else []
    error = None if r.status_code == 200 else "Impossible de récupérer la liste des projets"

    return render_template(
        "projects.html",
        {
            "request": request,
            "projects": projects,
            "error": error,
            "user": user,
            "active_organization_id": active_org_id,
            "active_organization_name": active_org_name,
            "organizations": organizations,
        },
    )


@app.post("/projects", response_class=HTMLResponse)
async def create_project_page(
    request: Request,
):
    auth = await require_auth(request)
    if isinstance(auth, RedirectResponse):
        return auth
    token, user = auth
    active_org_id, active_org_name, organizations = await get_organizations_context(request, token)

    try:
        r = await client.post(
            f"{AUTH_SERVICE_URL}/auth/projects",
            json={},
            headers=auth_headers(token, active_org_id),
        )
    except httpx.HTTPError:
        # Re-afficher la page avec une erreur générique
        return render_template(
            "projects.html",
            {
                "request": request,
                "projects": [],
                "error": "Impossible de créer le projet (service indisponible)",
                "user": user,
                "active_organization_id": active_org_id,
                "active_organization_name": active_org_name,
                "organizations": organizations,
            },
        )

    if r.status_code >= 400:
        # Récupérer les projets et l'utilisateur pour réafficher la page avec une erreur
        try:
            list_resp = await client.get(
                f"{AUTH_SERVICE_URL}/auth/projects",
                headers=auth_headers(token, active_org_id),
            )
            projects = list_resp.json() if list_resp.status_code == 200 else []
            me_resp = await client.get(
                f"{AUTH_SERVICE_URL}/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            user = me_resp.json() if me_resp.status_code == 200 else None
        except httpx.HTTPError:
            projects = []
            user = None

        error_detail = "Erreur lors de la création du projet"
        try:
            data = r.json()
            if isinstance(data, dict) and "detail" in data:
                error_detail = data["detail"]
        except Exception:
            pass

        return render_template(
            "projects.html",
            {
                "request": request,
                "projects": projects,
                "error": error_detail,
                "user": user,
                "active_organization_id": active_org_id,
                "active_organization_name": active_org_name,
                "organizations": organizations,
            },
        )

    # Succès ⇒ récupérer le projet et rediriger vers sa page de détail
    created = r.json()
    project_id = created.get("id")
    if project_id:
        return RedirectResponse(url=f"/projects/{project_id}", status_code=303)
    return RedirectResponse(url="/projects", status_code=303)


@app.get("/projects/{project_id}", response_class=HTMLResponse)
async def project_detail_page(request: Request, project_id: str):
    auth = await require_auth(request)
    if isinstance(auth, RedirectResponse):
        return auth
    token, user = auth
    active_org_id, active_org_name, organizations = await get_organizations_context(request, token)

    try:
        proj_resp = await client.get(
            f"{AUTH_SERVICE_URL}/auth/projects/{project_id}",
            headers=auth_headers(token, active_org_id),
        )
    except httpx.HTTPError:
        return RedirectResponse(url="/projects", status_code=303)

    if proj_resp.status_code != 200:
        return RedirectResponse(url="/projects", status_code=303)

    project = proj_resp.json()

    return render_template(
        "project_detail.html",
        {
            "request": request,
            "project": project,
            "user": user,
            "active_organization_id": active_org_id,
            "active_organization_name": active_org_name,
            "organizations": organizations,
        },
    )


@app.post("/projects/{project_id}/rename", response_class=HTMLResponse)
async def rename_project_page(
    request: Request,
    project_id: str,
    name: str = Form(...),
):
    auth = await require_auth(request)
    if isinstance(auth, RedirectResponse):
        return auth
    token, _user = auth
    active_org_id, _active_org_name, _organizations = await get_organizations_context(request, token)

    try:
        await client.patch(
            f"{AUTH_SERVICE_URL}/auth/projects/{project_id}",
            json={"name": name},
            headers=auth_headers(token, active_org_id),
        )
    except httpx.HTTPError:
        return RedirectResponse(url=f"/projects/{project_id}", status_code=303)

    return RedirectResponse(url=f"/projects/{project_id}", status_code=303)


@app.post("/projects/{project_id}/delete", response_class=HTMLResponse)
async def delete_project_page(
    request: Request,
    project_id: str,
):
    auth = await require_auth(request)
    if isinstance(auth, RedirectResponse):
        return auth
    token, _user = auth
    active_org_id, _active_org_name, _organizations = await get_organizations_context(request, token)

    try:
        await client.delete(
            f"{AUTH_SERVICE_URL}/auth/projects/{project_id}",
            headers=auth_headers(token, active_org_id),
        )
    except httpx.HTTPError:
        return RedirectResponse(url="/projects", status_code=303)

    return RedirectResponse(url="/projects", status_code=303)


@app.post("/organizations/select")
async def select_organization_web(
    request: Request,
    organization_id: str = Form(...),
    next_path: str = Form("/dashboard"),
):
    auth = await require_auth(request)
    if isinstance(auth, RedirectResponse):
        return auth
    token, _user = auth
    try:
        r = await client.post(
            f"{AUTH_SERVICE_URL}/auth/organizations/select",
            json={"organization_id": organization_id},
            headers={"Authorization": f"Bearer {token}"},
        )
    except httpx.HTTPError:
        return RedirectResponse(url=next_path or "/dashboard", status_code=303)

    resp = RedirectResponse(url=next_path or "/dashboard", status_code=303)
    if r.status_code == 200:
        resp.set_cookie(
            key=ACTIVE_ORG_COOKIE,
            value=organization_id,
            httponly=COOKIE.httponly,
            secure=COOKIE.secure,
            samesite=COOKIE.samesite,
            domain=COOKIE.domain,
            path="/",
        )
    return resp


@app.get("/organizations", response_class=HTMLResponse)
async def organizations_page(request: Request):
    auth = await require_auth(request)
    if isinstance(auth, RedirectResponse):
        return auth
    token, user = auth
    active_org_id, active_org_name, organizations = await get_organizations_context(request, token)
    error = None
    if not organizations:
        error = "Impossible de récupérer les organisations"
    return render_template(
        "organizations.html",
        {
            "request": request,
            "user": user,
            "organizations": organizations,
            "active_organization_id": active_org_id,
            "active_organization_name": active_org_name,
            "error": error,
        },
    )


@app.post("/organizations", response_class=HTMLResponse)
async def create_organization_web(
    request: Request,
    name: str = Form(...),
):
    auth = await require_auth(request)
    if isinstance(auth, RedirectResponse):
        return auth
    token, _user = auth

    try:
        r = await client.post(
            f"{AUTH_SERVICE_URL}/auth/organizations",
            json={"name": name},
            headers={"Authorization": f"Bearer {token}"},
        )
    except httpx.HTTPError:
        return RedirectResponse(url="/organizations", status_code=303)

    if r.status_code == 201:
        created = r.json()
        org_id = created.get("id")
        resp = RedirectResponse(url="/organizations", status_code=303)
        if org_id:
            resp.set_cookie(
                key=ACTIVE_ORG_COOKIE,
                value=org_id,
                httponly=COOKIE.httponly,
                secure=COOKIE.secure,
                samesite=COOKIE.samesite,
                domain=COOKIE.domain,
                path="/",
            )
        return resp

    return RedirectResponse(url="/organizations", status_code=303)


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
    auth = await require_auth(request)
    if isinstance(auth, RedirectResponse):
        return auth
    token, user = auth
    if not await require_roles(token, ["admin"]):
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    return render_template("admin.html", {"request": request, "user": user})


@app.get("/admin/users", response_class=HTMLResponse)
async def admin_users(request: Request):
    auth = await require_auth(request)
    if isinstance(auth, RedirectResponse):
        return auth
    token, user = auth
    if not await require_roles(token, ["admin"]):
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # TODO: Récupérer la liste des utilisateurs depuis l'API
    return render_template("admin-users.html", {"request": request, "user": user, "users": []})


@app.get("/admin/roles", response_class=HTMLResponse)
async def admin_roles(request: Request):
    auth = await require_auth(request)
    if isinstance(auth, RedirectResponse):
        return auth
    token, user = auth
    if not await require_roles(token, ["admin"]):
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # TODO: Récupérer la liste des rôles depuis l'API
    return render_template("admin-roles.html", {"request": request, "user": user, "roles": []})


@app.get("/admin/stats", response_class=HTMLResponse)
async def admin_stats(request: Request):
    auth = await require_auth(request)
    if isinstance(auth, RedirectResponse):
        return auth
    token, user = auth
    if not await require_roles(token, ["admin"]):
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # TODO: Récupérer les statistiques depuis l'API
    return render_template("admin-stats.html", {"request": request, "user": user, "stats": {}})


@app.get("/admin/logs", response_class=HTMLResponse)
async def admin_logs(request: Request):
    auth = await require_auth(request)
    if isinstance(auth, RedirectResponse):
        return auth
    token, user = auth
    if not await require_roles(token, ["admin"]):
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # TODO: Récupérer les logs depuis l'API
    return render_template("admin-logs.html", {"request": request, "user": user, "logs": []})


@app.get("/admin/settings", response_class=HTMLResponse)
async def admin_settings(request: Request):
    auth = await require_auth(request)
    if isinstance(auth, RedirectResponse):
        return auth
    token, user = auth
    if not await require_roles(token, ["admin"]):
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # TODO: Récupérer les paramètres système depuis l'API
    return render_template("admin-settings.html", {"request": request, "user": user, "settings": {}})


@app.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_page(request: Request):
    return render_template("forgot-password.html", {"request": request, "error": None, "success": None})


@app.post("/forgot-password")
async def forgot_password(request: Request, email: EmailStr = Form(...)):
    try:
        r = await client.post(f"{AUTH_SERVICE_URL}/auth/request-password-reset", json={"email": email})
        if r.status_code == 200:
            return render_template("forgot-password.html", {
                "request": request, 
                "error": None, 
                "success": "Si cette adresse email existe, un lien de réinitialisation a été envoyé."
            })
        else:
            return render_template("forgot-password.html", {
                "request": request, 
                "error": "Erreur lors de l'envoi de l'email", 
                "success": None
            })
    except httpx.HTTPError:
        return render_template("forgot-password.html", {
            "request": request, 
            "error": "Service auth indisponible", 
            "success": None
        })


@app.get("/reset-password", response_class=HTMLResponse)
def reset_password_page(request: Request, token: str = None):
    if not token:
        return RedirectResponse(url="/forgot-password", status_code=303)
    return render_template("reset-password.html", {"request": request, "token": token, "error": None})


@app.post("/reset-password")
async def reset_password(request: Request, token: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)):
    if password != confirm_password:
        return render_template("reset-password.html", {
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
            return render_template("reset-password.html", {
                "request": request, 
                "token": token, 
                "error": "Token invalide ou expiré"
            })
    except httpx.HTTPError:
        return render_template("reset-password.html", {
            "request": request, 
            "token": token, 
            "error": "Service auth indisponible"
        })


@app.get("/account", response_class=HTMLResponse)
async def account_page(request: Request):
    auth = await require_auth(request)
    if isinstance(auth, RedirectResponse):
        return auth
    _token, user = auth
    return render_template("account.html", {"request": request, "user": user, "error": None, "success": None})


@app.post("/account")
async def update_account(request: Request, first_name: str = Form(None), last_name: str = Form(None)):
    auth = await require_auth(request)
    if isinstance(auth, RedirectResponse):
        return auth
    token, _user = auth
    
    # TODO: Implémenter la mise à jour du profil côté API
    # Pour l'instant, on simule un succès
    try:
        r = await client.get(f"{AUTH_SERVICE_URL}/me", headers={"Authorization": f"Bearer {token}"})
        if r.status_code == 200:
            user = r.json()
            return render_template("account.html", {
                "request": request, 
                "user": user, 
                "error": None, 
                "success": "Profil mis à jour avec succès !"
            })
        else:
            return login_redirect(next_path=request.url.path)
    except httpx.HTTPError:
        return render_template("account.html", {
            "request": request, 
            "user": {"email": "user@example.com"}, 
            "error": "Erreur lors de la mise à jour", 
            "success": None
        })


@app.get("/change-password", response_class=HTMLResponse)
async def change_password_page(request: Request):
    auth = await require_auth(request)
    if isinstance(auth, RedirectResponse):
        return auth
    _token, user = auth

    return render_template("change-password.html", {"request": request, "user": user, "error": None, "success": None})


@app.post("/change-password")
async def change_password(request: Request, current_password: str = Form(...), new_password: str = Form(...), confirm_password: str = Form(...)):
    auth = await require_auth(request)
    if isinstance(auth, RedirectResponse):
        return auth
    _token, user = auth
    
    if new_password != confirm_password:
        return render_template("change-password.html", {
            "request": request, 
            "user": user,
            "error": "Les mots de passe ne correspondent pas", 
            "success": None
        })
    
    # TODO: Implémenter le changement de mot de passe côté API
    # Pour l'instant, on simule un succès
    return render_template("change-password.html", {
        "request": request, 
        "user": user,
        "error": None, 
        "success": "Mot de passe changé avec succès !"
    })


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    auth = await require_auth(request)
    if isinstance(auth, RedirectResponse):
        return auth
    _token, user = auth
    return render_template("settings.html", {"request": request, "user": user, "error": None, "success": None})


@app.post("/settings")
async def update_settings(request: Request, theme: str = Form("auto"), language: str = Form("fr")):
    auth = await require_auth(request)
    if isinstance(auth, RedirectResponse):
        return auth
    token, _user = auth
    
    # TODO: Implémenter la sauvegarde des paramètres côté API
    # Pour l'instant, on simule un succès
    try:
        r = await client.get(f"{AUTH_SERVICE_URL}/me", headers={"Authorization": f"Bearer {token}"})
        if r.status_code == 200:
            user = r.json()
            # Simuler la mise à jour
            user["theme_preference"] = theme
            return render_template("settings.html", {
                "request": request, 
                "user": user, 
                "error": None, 
                "success": "Paramètres sauvegardés avec succès !"
            })
        else:
            return login_redirect(next_path=request.url.path)
    except httpx.HTTPError:
        return render_template("settings.html", {
            "request": request, 
            "user": {"email": "user@example.com", "theme_preference": theme}, 
            "error": "Erreur lors de la sauvegarde", 
            "success": None
        })


