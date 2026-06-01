"""User account area: profile, order history, quote history."""
import logging

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from database import get_db
from models import Order, QuoteRequest, User
from security import get_current_user, verify_password, hash_password
from ._common import templates, base_ctx

logger = logging.getLogger("aquaterra.account")

router = APIRouter(prefix="/account")


@router.get("")
@router.get("/")
def account_home(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login?next=/account", status_code=303)
    orders = (
        db.query(Order)
        .filter(or_(Order.user_id == user.id, Order.buyer_email == user.email))
        .order_by(Order.id.desc())
        .all()
    )
    quotes = (
        db.query(QuoteRequest)
        .filter(QuoteRequest.email == user.email)
        .order_by(QuoteRequest.id.desc())
        .all()
    )
    return templates.TemplateResponse(
        "account.html",
        base_ctx(request, account=user, orders=orders, quotes=quotes, msg=request.query_params.get("msg")),
    )


@router.post("/update")
def account_update(
    request: Request,
    db: Session = Depends(get_db),
    full_name: str = Form(""),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    user.full_name = full_name.strip()
    db.commit()
    return RedirectResponse(url="/account?msg=profile", status_code=303)


@router.post("/password")
def account_password(
    request: Request,
    db: Session = Depends(get_db),
    current_password: str = Form(...),
    new_password: str = Form(...),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    if not verify_password(current_password, user.password_hash):
        return RedirectResponse(url="/account?msg=badpass", status_code=303)
    if len(new_password) < 6:
        return RedirectResponse(url="/account?msg=shortpass", status_code=303)
    user.password_hash = hash_password(new_password)
    db.commit()
    logger.info("[ACCOUNT] password changed user_id=%s", user.id)
    return RedirectResponse(url="/account?msg=password", status_code=303)
