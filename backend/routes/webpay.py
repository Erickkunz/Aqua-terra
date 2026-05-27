"""WebPay Plus (Transbank) checkout integration.

Uses Transbank integration credentials by default. To switch to production,
set TRANSBANK_ENV=production, TRANSBANK_COMMERCE_CODE, TRANSBANK_API_KEY.

Flow:
  1. User clicks "Pagar con WebPay" on /shop/cart -> POST /checkout/webpay/create
  2. We create an Order row (status=pending), call WebPay create_transaction,
     redirect the user to the WebPay hosted form.
  3. WebPay redirects back to /webpay/return with token_ws.
  4. We commit the transaction, update the Order, render /webpay/success or /webpay/failed.
"""
from __future__ import annotations

import logging
import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from database import get_db
from models import Order, Product
from utils import best_bulk_discount
from ._common import templates, base_ctx
from config import settings

# Transbank SDK
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_type import IntegrationType
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys

logger = logging.getLogger("aquaterra.webpay")

router = APIRouter()


def _get_transaction() -> Transaction:
    """Build a Transaction client using settings (integration by default)."""
    env = (getattr(settings, "TRANSBANK_ENV", "integration") or "integration").lower()
    if env == "production":
        commerce_code = getattr(settings, "TRANSBANK_COMMERCE_CODE", "")
        api_key = getattr(settings, "TRANSBANK_API_KEY", "")
        if not commerce_code or not api_key:
            raise RuntimeError("Falta TRANSBANK_COMMERCE_CODE / TRANSBANK_API_KEY")
        opts = WebpayOptions(commerce_code, api_key, IntegrationType.LIVE)
    else:
        opts = WebpayOptions(
            IntegrationCommerceCodes.WEBPAY_PLUS,
            IntegrationApiKeys.WEBPAY,
            IntegrationType.TEST,
        )
    return Transaction(opts)


def _build_return_url(request: Request) -> str:
    """Public URL where Transbank should POST back after payment."""
    scheme = request.url.scheme
    host = request.headers.get("host") or request.url.netloc
    forwarded_proto = request.headers.get("x-forwarded-proto")
    if forwarded_proto:
        scheme = forwarded_proto.split(",")[0].strip()
    return f"{scheme}://{host}/webpay/return"


@router.post("/checkout/webpay/create")
async def webpay_create(request: Request, db: Session = Depends(get_db)):
    """Create a WebPay transaction from the current cart and redirect to it."""
    form = await request.form()
    buyer_name = (form.get("buyer_name") or "").strip()
    buyer_email = (form.get("buyer_email") or "").strip()
    buyer_phone = (form.get("buyer_phone") or "").strip()
    buyer_address = (form.get("buyer_address") or "").strip()

    cart = request.session.get("cart") or {}
    if not isinstance(cart, dict) or not cart:
        raise HTTPException(400, "El carrito esta vacio.")

    ids = [int(i) for i in cart.keys() if str(i).isdigit()]
    products = {p.id: p for p in db.query(Product).filter(Product.id.in_(ids)).all()}

    items_snapshot = []
    subtotal = 0.0
    for pid_str, qty in cart.items():
        try:
            pid = int(pid_str)
        except ValueError:
            continue
        p = products.get(pid)
        if not p:
            continue
        qty = int(qty)
        discount = best_bulk_discount(qty, p.bulk_discount)
        line = p.price * qty * (1 - discount)
        subtotal += line
        items_snapshot.append({
            "product_id": p.id, "name": p.name, "qty": qty,
            "unit_price": p.price, "discount": discount, "line_total": line,
        })

    if subtotal <= 0:
        raise HTTPException(400, "Total invalido para procesar pago.")

    # Buy order: short, unique, max 26 chars for WebPay Plus
    buy_order = "AT" + secrets.token_hex(8).upper()  # AT + 16 hex = 18 chars
    session_id = "SID" + secrets.token_hex(6).upper()

    # WebPay only accepts integer amounts in CLP. Round to nearest CLP.
    amount_clp = int(round(subtotal))

    order = Order(
        user_id=request.session.get("user_id"),
        buyer_name=buyer_name,
        buyer_email=buyer_email,
        buyer_phone=buyer_phone,
        buyer_address=buyer_address,
        subtotal=subtotal,
        total=amount_clp,
        currency="CLP",
        buy_order=buy_order,
        session_id=session_id,
        items_snapshot=items_snapshot,
        status="pending",
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    return_url = _build_return_url(request)

    try:
        tx = _get_transaction()
        response = tx.create(buy_order, session_id, amount_clp, return_url)
    except Exception as e:
        logger.exception("[WEBPAY] create failed for order %s: %s", buy_order, e)
        order.status = "failed"
        db.commit()
        raise HTTPException(502, f"Error iniciando WebPay: {e}")

    # response = { 'token': ..., 'url': ... }
    token = response.get("token") if isinstance(response, dict) else response["token"]
    url = response.get("url") if isinstance(response, dict) else response["url"]
    order.webpay_token = token
    db.commit()

    logger.info("[WEBPAY] tx created order=%s token=%s amount=%s", buy_order, token, amount_clp)

    # Auto-submitting form (WebPay requires a POST with token_ws)
    html = f"""
    <!doctype html>
    <html><head><meta charset="utf-8"><title>Redirigiendo a WebPay...</title></head>
    <body style="font-family:system-ui;text-align:center;padding:3rem">
      <h2>Redirigiendo a WebPay...</h2>
      <p>Si no eres redirigido automaticamente, haz click en el boton.</p>
      <form id="wp" method="POST" action="{url}">
        <input type="hidden" name="token_ws" value="{token}" />
        <button type="submit" style="padding:.8rem 1.4rem;font-size:1rem">Continuar</button>
      </form>
      <script>document.getElementById('wp').submit();</script>
    </body></html>
    """
    return HTMLResponse(html)


@router.api_route("/webpay/return", methods=["GET", "POST"])
async def webpay_return(request: Request, db: Session = Depends(get_db)):
    """Callback from WebPay after the user finishes (or aborts) the payment."""
    form = await request.form()
    qp = dict(request.query_params)

    token_ws = form.get("token_ws") or qp.get("token_ws")
    tbk_token = form.get("TBK_TOKEN") or qp.get("TBK_TOKEN")
    tbk_orden_compra = form.get("TBK_ORDEN_COMPRA") or qp.get("TBK_ORDEN_COMPRA")

    # User aborted the payment in Transbank UI
    if tbk_token and not token_ws:
        order = db.query(Order).filter(Order.buy_order == tbk_orden_compra).first()
        if order:
            order.status = "aborted"
            db.commit()
        logger.info("[WEBPAY] aborted by user order=%s", tbk_orden_compra)
        return templates.TemplateResponse(
            "webpay_failed.html",
            base_ctx(request, reason="Pago cancelado por el usuario", order=order),
        )

    if not token_ws:
        return templates.TemplateResponse(
            "webpay_failed.html",
            base_ctx(request, reason="Sin token de WebPay", order=None),
        )

    order = db.query(Order).filter(Order.webpay_token == token_ws).first()
    if not order:
        return templates.TemplateResponse(
            "webpay_failed.html",
            base_ctx(request, reason="Orden no encontrada", order=None),
        )

    # Commit the transaction
    try:
        tx = _get_transaction()
        result = tx.commit(token_ws)
    except Exception as e:
        logger.exception("[WEBPAY] commit failed token=%s: %s", token_ws, e)
        order.status = "failed"
        db.commit()
        return templates.TemplateResponse(
            "webpay_failed.html",
            base_ctx(request, reason=f"Error confirmando: {e}", order=order),
        )

    # Normalize result (SDK returns a dict-like)
    def g(k):
        if isinstance(result, dict):
            return result.get(k)
        return getattr(result, k, None)

    response_code = g("response_code")
    order.webpay_response_code = response_code if response_code is not None else None
    order.webpay_authorization_code = g("authorization_code") or ""
    order.webpay_payment_type = g("payment_type_code") or ""
    last4 = g("card_detail")
    if isinstance(last4, dict):
        order.webpay_card_last4 = (last4.get("card_number") or "")[-4:]

    if response_code == 0:
        order.status = "paid"
        order.paid_at = datetime.utcnow()
        request.session["cart"] = {}  # clear cart on success
        db.commit()
        logger.info("[WEBPAY] PAID order=%s auth=%s", order.buy_order, order.webpay_authorization_code)
        return templates.TemplateResponse(
            "webpay_success.html",
            base_ctx(request, order=order, result=result),
        )

    order.status = "failed"
    db.commit()
    logger.info("[WEBPAY] FAILED order=%s code=%s", order.buy_order, response_code)
    return templates.TemplateResponse(
        "webpay_failed.html",
        base_ctx(request, reason=f"Pago rechazado (codigo {response_code})", order=order),
    )


@router.get("/checkout")
def checkout_page(request: Request, db: Session = Depends(get_db)):
    """Lightweight checkout page that collects buyer info and shows the WebPay button."""
    cart = request.session.get("cart") or {}
    if not isinstance(cart, dict) or not cart:
        return RedirectResponse(url="/shop/cart", status_code=303)
    ids = [int(i) for i in cart.keys() if str(i).isdigit()]
    products = db.query(Product).filter(Product.id.in_(ids)).all()
    items = []
    subtotal = 0.0
    for p in products:
        qty = int(cart.get(str(p.id), 0))
        discount = best_bulk_discount(qty, p.bulk_discount)
        line = p.price * qty * (1 - discount)
        subtotal += line
        items.append({"product": p, "qty": qty, "discount": discount, "line_total": line})
    return templates.TemplateResponse(
        "checkout.html",
        base_ctx(request, items=items, subtotal=subtotal),
    )
