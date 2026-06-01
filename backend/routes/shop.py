from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from database import get_db
from models import Category, Product, QuoteRequest, ProductReview
from schemas import CartItemIn, QuoteIn
from security import get_current_user
from utils import best_bulk_discount
from ._common import templates, base_ctx

import logging

logger = logging.getLogger("aquaterra.shop")

router = APIRouter(prefix="/shop")


def _serialize_product_min(p: Product) -> dict:
    return {
        "id": p.id,
        "slug": p.slug,
        "name": p.name,
        "price": p.price,
        "currency": p.currency,
        "image_url": p.image_url,
        "in_stock": p.in_stock,
        "category": p.category.name if p.category else "",
    }


@router.get("")
def shop_index(
    request: Request,
    db: Session = Depends(get_db),
    category: str | None = None,
    search: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    in_stock: bool | None = None,
    sort: str = "featured",
    page: int = Query(1, ge=1),
):
    per_page = 12
    q = db.query(Product).join(Category)

    if category:
        q = q.filter(Category.slug == category)
    if search:
        like = f"%{search}%"
        q = q.filter(or_(Product.name.ilike(like), Product.short_description.ilike(like)))
    if min_price is not None:
        q = q.filter(Product.price >= min_price)
    if max_price is not None:
        q = q.filter(Product.price <= max_price)
    if in_stock is not None:
        q = q.filter(Product.in_stock == in_stock)

    if sort == "price_asc":
        q = q.order_by(Product.price.asc())
    elif sort == "price_desc":
        q = q.order_by(Product.price.desc())
    elif sort == "rating":
        q = q.order_by(Product.rating.desc())
    elif sort == "name":
        q = q.order_by(Product.name.asc())
    else:
        q = q.order_by(Product.is_featured.desc(), Product.rating.desc())

    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    categories = db.query(Category).order_by(Category.name).all()
    pages = max(1, (total + per_page - 1) // per_page)

    return templates.TemplateResponse(
        "shop.html",
        base_ctx(
            request,
            products=items,
            categories=categories,
            total=total,
            page=page,
            pages=pages,
            filters={
                "category": category or "",
                "search": search or "",
                "min_price": min_price,
                "max_price": max_price,
                "in_stock": in_stock,
                "sort": sort,
            },
        ),
    )


@router.get("/api/products")
def api_products(
    db: Session = Depends(get_db),
    category: str | None = None,
    search: str | None = None,
    limit: int = Query(12, ge=1, le=60),
):
    q = db.query(Product).join(Category)
    if category:
        q = q.filter(Category.slug == category)
    if search:
        like = f"%{search}%"
        q = q.filter(or_(Product.name.ilike(like), Product.short_description.ilike(like)))
    items = q.limit(limit).all()
    return {"items": [_serialize_product_min(p) for p in items]}


@router.get("/products/{slug}")
def product_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.slug == slug).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    related = (
        db.query(Product)
        .filter(Product.category_id == product.category_id, Product.id != product.id)
        .limit(4)
        .all()
    )
    reviews = (
        db.query(ProductReview)
        .filter(ProductReview.product_id == product.id)
        .order_by(ProductReview.id.desc())
        .all()
    )
    return templates.TemplateResponse(
        "product_detail.html",
        base_ctx(request, product=product, related=related, reviews=reviews),
    )


@router.post("/products/{pid}/review")
def add_review(
    pid: int,
    request: Request,
    db: Session = Depends(get_db),
    rating: int = Form(5),
    text: str = Form(""),
):
    user = get_current_user(request, db)
    product = db.query(Product).filter(Product.id == pid).first()
    if not product:
        raise HTTPException(404, "Producto no encontrado")
    if not user:
        return RedirectResponse(url=f"/login?next=/shop/products/{product.slug}", status_code=303)

    rating = max(1, min(5, int(rating)))
    review = ProductReview(
        product_id=pid,
        author=user.full_name or user.username,
        rating=rating,
        text=text.strip()[:2000],
    )
    db.add(review)
    db.flush()
    # Recalculate the product's average rating and review count
    revs = db.query(ProductReview).filter(ProductReview.product_id == pid).all()
    if revs:
        product.rating = round(sum(r.rating for r in revs) / len(revs), 1)
        product.reviews_count = len(revs)
    db.commit()
    logger.info("[REVIEW] product=%s user=%s rating=%s", pid, user.id, rating)
    return RedirectResponse(url=f"/shop/products/{product.slug}#reviews", status_code=303)


@router.post("/cart/add")
def cart_add(payload: CartItemIn, request: Request, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    cart = request.session.get("cart", {})
    if not isinstance(cart, dict):
        cart = {}
    pid = str(payload.product_id)
    cart[pid] = cart.get(pid, 0) + payload.qty
    request.session["cart"] = cart

    total_items = sum(cart.values())
    return {"ok": True, "cart_count": total_items, "product": product.name}


@router.post("/cart/remove")
def cart_remove(payload: CartItemIn, request: Request):
    cart = request.session.get("cart", {})
    cart.pop(str(payload.product_id), None)
    request.session["cart"] = cart
    return {"ok": True, "cart_count": sum(cart.values())}


@router.post("/cart/update")
def cart_update(payload: CartItemIn, request: Request):
    cart = request.session.get("cart", {})
    if payload.qty <= 0:
        cart.pop(str(payload.product_id), None)
    else:
        cart[str(payload.product_id)] = payload.qty
    request.session["cart"] = cart
    return {"ok": True, "cart_count": sum(cart.values())}


@router.get("/cart")
def cart_view(request: Request, db: Session = Depends(get_db)):
    cart = request.session.get("cart", {})
    items = []
    subtotal = 0.0
    if isinstance(cart, dict) and cart:
        ids = [int(i) for i in cart.keys()]
        products = db.query(Product).filter(Product.id.in_(ids)).all()
        for p in products:
            qty = cart.get(str(p.id), 0)
            discount = best_bulk_discount(qty, p.bulk_discount)
            line = p.price * qty * (1 - discount)
            subtotal += line
            items.append({"product": p, "qty": qty, "discount": discount, "line_total": line})
    return templates.TemplateResponse(
        "cart.html",
        base_ctx(request, items=items, subtotal=subtotal),
    )


@router.post("/wishlist/toggle")
def wishlist_toggle(payload: CartItemIn, request: Request):
    wishlist = request.session.get("wishlist", [])
    pid = payload.product_id
    if pid in wishlist:
        wishlist.remove(pid)
        added = False
    else:
        wishlist.append(pid)
        added = True
    request.session["wishlist"] = wishlist
    return {"ok": True, "added": added, "count": len(wishlist)}


@router.get("/wishlist")
def wishlist_view(request: Request, db: Session = Depends(get_db)):
    wishlist = request.session.get("wishlist", [])
    products = []
    if wishlist:
        products = db.query(Product).filter(Product.id.in_(wishlist)).all()
    return templates.TemplateResponse(
        "wishlist.html",
        base_ctx(request, products=products),
    )


@router.get("/compare")
def compare_view(request: Request, db: Session = Depends(get_db), ids: str = ""):
    products = []
    if ids:
        try:
            id_list = [int(i) for i in ids.split(",") if i.strip()][:4]
            products = db.query(Product).filter(Product.id.in_(id_list)).all()
        except ValueError:
            products = []
    return templates.TemplateResponse(
        "compare.html",
        base_ctx(request, products=products),
    )


@router.post("/quote", response_class=JSONResponse)
def submit_quote(payload: QuoteIn, request: Request, db: Session = Depends(get_db)):
    ids = [item.product_id for item in payload.items]
    products = {p.id: p for p in db.query(Product).filter(Product.id.in_(ids)).all()}

    items_snapshot = []
    estimated_total = 0.0
    for item in payload.items:
        p = products.get(item.product_id)
        if not p:
            continue
        discount = best_bulk_discount(item.qty, p.bulk_discount)
        line = p.price * item.qty * (1 - discount)
        estimated_total += line
        items_snapshot.append({
            "product_id": p.id,
            "name": p.name,
            "qty": item.qty,
            "unit_price": p.price,
            "discount": discount,
            "line_total": line,
        })

    quote = QuoteRequest(
        name=payload.name,
        email=payload.email,
        company=payload.company,
        phone=payload.phone,
        country=payload.country,
        items=items_snapshot,
        estimated_total=estimated_total,
        notes=payload.notes,
    )
    db.add(quote)
    db.commit()
    db.refresh(quote)

    logger.info("[QUOTE] #%s %s <%s> total=%.2f", quote.id, payload.name, payload.email, estimated_total)
    request.session["cart"] = {}

    return {"ok": True, "quote_id": quote.id, "estimated_total": estimated_total}
