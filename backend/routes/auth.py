"""Auth routes: register, login, logout, profile."""
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from security import hash_password, verify_password, get_current_user
from ._common import templates, base_ctx

logger = logging.getLogger("aquaterra.auth")

router = APIRouter()


# ---- Pages ----
@router.get("/login")
def login_page(request: Request, db: Session = Depends(get_db), next: str = "/"):
    if get_current_user(request, db):
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse(
        "auth/login.html",
        base_ctx(request, next_url=next, error=None),
    )


@router.get("/register")
def register_page(request: Request, db: Session = Depends(get_db)):
    if get_current_user(request, db):
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse(
        "auth/register.html",
        base_ctx(request, error=None, values={}),
    )


# ---- Form handlers ----
@router.post("/login")
@limiter.limit("10/minute")
def login_submit(
    request: Request,
    db: Session = Depends(get_db),
    username: str = Form(...),
    password: str = Form(...),
    next: str = Form("/"),
):
    ident = username.strip().lower()
    user = db.query(User).filter(
        or_(User.username == ident, User.email == ident)
    ).first()

    if not user or not user.is_active or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "auth/login.html",
            base_ctx(request, error="Usuario o contrasena invalidos.", next_url=next),
            status_code=400,
        )

    user.last_login = datetime.utcnow()
    db.commit()

    # Reset session entirely on login (prevents session fixation + ensures
    # cart/wishlist from a previous account don't carry over).
    request.session.clear()
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    request.session["is_admin"] = bool(user.is_admin)
    logger.info("[LOGIN] user_id=%s username=%s admin=%s", user.id, user.username, user.is_admin)

    return RedirectResponse(url=_safe_next(next), status_code=303)


@router.post("/register")
@limiter.limit("5/minute")
def register_submit(
    request: Request,
    db: Session = Depends(get_db),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(""),
):
    username = username.strip().lower()
    email = email.strip().lower()
    values = {"username": username, "email": email, "full_name": full_name}

    if len(username) < 3 or not all(c.isalnum() or c in "_.-" for c in username):
        return templates.TemplateResponse(
            "auth/register.html",
            base_ctx(request, error="Usuario invalido (min 3, solo letras, numeros, _ . -).", values=values),
            status_code=400,
        )
    if "@" not in email or len(email) < 5:
        return templates.TemplateResponse(
            "auth/register.html",
            base_ctx(request, error="Email invalido.", values=values),
            status_code=400,
        )
    if len(password) < 6:
        return templates.TemplateResponse(
            "auth/register.html",
            base_ctx(request, error="La contrasena debe tener al menos 6 caracteres.", values=values),
            status_code=400,
        )

    exists = db.query(User).filter(
        or_(User.username == username, User.email == email)
    ).first()
    if exists:
        return templates.TemplateResponse(
            "auth/register.html",
            base_ctx(request, error="Usuario o email ya registrados.", values=values),
            status_code=400,
        )

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        full_name=full_name.strip(),
        is_admin=False,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Reset session entirely on register: new account starts clean.
    request.session.clear()
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    request.session["is_admin"] = False
    logger.info("[REGISTER] new user_id=%s username=%s", user.id, user.username)

    return RedirectResponse(url="/", status_code=303)


@router.post("/logout")
@router.get("/logout")
def logout(request: Request):
    # Wipe the session entirely on logout. This guarantees that cart, wishlist
    # and any other transient state DO NOT leak to whoever logs in next on
    # the same browser. Each account starts with a clean session.
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)
