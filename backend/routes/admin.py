"""Admin panel: CRUD for products, projects, blog posts, testimonials, categories, users."""
import json
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from database import get_db
from models import (
    Category, Product, Project, Testimonial, BlogPost,
    ContactSubmission, QuoteRequest, NewsletterSubscriber, User,
)
from security import require_admin, hash_password
from utils import slugify
from ._common import templates, base_ctx

logger = logging.getLogger("aquaterra.admin")

router = APIRouter(prefix="/admin")


# ---- Dashboard ----
@router.get("")
@router.get("/")
def admin_home(request: Request, db: Session = Depends(get_db)):
    admin = require_admin(request, db)
    stats = {
        "users": db.query(User).count(),
        "products": db.query(Product).count(),
        "categories": db.query(Category).count(),
        "projects": db.query(Project).count(),
        "posts": db.query(BlogPost).count(),
        "testimonials": db.query(Testimonial).count(),
        "contacts": db.query(ContactSubmission).count(),
        "quotes": db.query(QuoteRequest).count(),
        "subscribers": db.query(NewsletterSubscriber).count(),
    }
    recent_contacts = db.query(ContactSubmission).order_by(ContactSubmission.id.desc()).limit(5).all()
    recent_quotes = db.query(QuoteRequest).order_by(QuoteRequest.id.desc()).limit(5).all()
    return templates.TemplateResponse(
        "admin/dashboard.html",
        base_ctx(request, admin=admin, stats=stats, recent_contacts=recent_contacts, recent_quotes=recent_quotes),
    )


# ===== PRODUCTS =====
@router.get("/products")
def admin_products(request: Request, db: Session = Depends(get_db)):
    require_admin(request, db)
    items = db.query(Product).order_by(Product.id.desc()).all()
    cats = db.query(Category).order_by(Category.name).all()
    return templates.TemplateResponse(
        "admin/products.html",
        base_ctx(request, items=items, cats=cats),
    )


@router.get("/products/new")
def product_new_page(request: Request, db: Session = Depends(get_db)):
    require_admin(request, db)
    cats = db.query(Category).order_by(Category.name).all()
    return templates.TemplateResponse(
        "admin/product_form.html",
        base_ctx(request, item=None, cats=cats),
    )


@router.get("/products/{pid}/edit")
def product_edit_page(pid: int, request: Request, db: Session = Depends(get_db)):
    require_admin(request, db)
    item = db.query(Product).filter(Product.id == pid).first()
    if not item:
        raise HTTPException(404, "Producto no encontrado")
    cats = db.query(Category).order_by(Category.name).all()
    return templates.TemplateResponse(
        "admin/product_form.html",
        base_ctx(request, item=item, cats=cats),
    )


def _parse_json_field(raw: str, default):
    if not raw or not raw.strip():
        return default
    try:
        return json.loads(raw)
    except Exception:
        return default


@router.post("/products/save")
def product_save(
    request: Request,
    db: Session = Depends(get_db),
    id: str = Form(""),
    name: str = Form(...),
    category_id: int = Form(...),
    price: float = Form(0.0),
    currency: str = Form("USD"),
    image_url: str = Form(""),
    short_description: str = Form(""),
    description: str = Form(""),
    in_stock: str = Form("on"),
    is_featured: str = Form(""),
    rating: float = Form(4.5),
    stock_qty: int = Form(10),
    specifications_json: str = Form("{}"),
    features_json: str = Form("[]"),
):
    require_admin(request, db)
    is_new = not id.strip()
    if is_new:
        item = Product(slug=slugify(name), category_id=category_id, name=name)
        db.add(item)
    else:
        item = db.query(Product).filter(Product.id == int(id)).first()
        if not item:
            raise HTTPException(404, "Producto no encontrado")

    item.name = name
    item.slug = slugify(name)
    item.category_id = category_id
    item.price = price
    item.currency = currency
    item.image_url = image_url
    item.short_description = short_description
    item.description = description
    item.in_stock = (in_stock == "on")
    item.is_featured = (is_featured == "on")
    item.rating = rating
    item.stock_qty = stock_qty
    item.specifications = _parse_json_field(specifications_json, {})
    item.features = _parse_json_field(features_json, [])

    db.commit()
    logger.info("[ADMIN] product %s id=%s", "created" if is_new else "updated", item.id)
    return RedirectResponse(url="/admin/products", status_code=303)


@router.post("/products/{pid}/delete")
def product_delete(pid: int, request: Request, db: Session = Depends(get_db)):
    require_admin(request, db)
    item = db.query(Product).filter(Product.id == pid).first()
    if item:
        db.delete(item)
        db.commit()
        logger.info("[ADMIN] product deleted id=%s", pid)
    return RedirectResponse(url="/admin/products", status_code=303)


# ===== CATEGORIES =====
@router.post("/categories/save")
def category_save(
    request: Request,
    db: Session = Depends(get_db),
    id: str = Form(""),
    name: str = Form(...),
    icon: str = Form("droplet"),
    description: str = Form(""),
):
    require_admin(request, db)
    if id.strip():
        cat = db.query(Category).filter(Category.id == int(id)).first()
        if not cat:
            raise HTTPException(404, "Categoria no encontrada")
    else:
        cat = Category(slug=slugify(name))
        db.add(cat)
    cat.name = name
    cat.slug = slugify(name)
    cat.icon = icon
    cat.description = description
    db.commit()
    return RedirectResponse(url="/admin/products", status_code=303)


@router.post("/categories/{cid}/delete")
def category_delete(cid: int, request: Request, db: Session = Depends(get_db)):
    require_admin(request, db)
    cat = db.query(Category).filter(Category.id == cid).first()
    if cat:
        db.delete(cat)
        db.commit()
    return RedirectResponse(url="/admin/products", status_code=303)


# ===== PROJECTS =====
@router.get("/projects")
def admin_projects(request: Request, db: Session = Depends(get_db)):
    require_admin(request, db)
    items = db.query(Project).order_by(Project.id.desc()).all()
    return templates.TemplateResponse(
        "admin/projects.html",
        base_ctx(request, items=items),
    )


@router.get("/projects/new")
def project_new(request: Request, db: Session = Depends(get_db)):
    require_admin(request, db)
    return templates.TemplateResponse(
        "admin/project_form.html",
        base_ctx(request, item=None),
    )


@router.get("/projects/{pid}/edit")
def project_edit(pid: int, request: Request, db: Session = Depends(get_db)):
    require_admin(request, db)
    item = db.query(Project).filter(Project.id == pid).first()
    if not item:
        raise HTTPException(404, "Proyecto no encontrado")
    return templates.TemplateResponse(
        "admin/project_form.html",
        base_ctx(request, item=item),
    )


@router.post("/projects/save")
def project_save(
    request: Request,
    db: Session = Depends(get_db),
    id: str = Form(""),
    name: str = Form(...),
    country: str = Form(""),
    region: str = Form(""),
    client_type: str = Form("agro"),
    technology: str = Form("drip"),
    summary: str = Form(""),
    description: str = Form(""),
    water_saved_m3: int = Form(0),
    hectares: int = Form(0),
    co2_reduced_t: int = Form(0),
    duration_months: int = Form(0),
    latitude: float = Form(0.0),
    longitude: float = Form(0.0),
    is_featured: str = Form(""),
):
    require_admin(request, db)
    if id.strip():
        item = db.query(Project).filter(Project.id == int(id)).first()
        if not item:
            raise HTTPException(404, "Proyecto no encontrado")
    else:
        item = Project(slug=slugify(name), name=name, completion_date=datetime.utcnow().date())
        db.add(item)
    item.name = name
    item.slug = slugify(name)
    item.country = country
    item.region = region
    item.client_type = client_type
    item.technology = technology
    item.summary = summary
    item.description = description
    item.water_saved_m3 = water_saved_m3
    item.hectares = hectares
    item.co2_reduced_t = co2_reduced_t
    item.duration_months = duration_months
    item.latitude = latitude
    item.longitude = longitude
    item.is_featured = 1 if is_featured == "on" else 0
    db.commit()
    return RedirectResponse(url="/admin/projects", status_code=303)


@router.post("/projects/{pid}/delete")
def project_delete(pid: int, request: Request, db: Session = Depends(get_db)):
    require_admin(request, db)
    item = db.query(Project).filter(Project.id == pid).first()
    if item:
        db.delete(item)
        db.commit()
    return RedirectResponse(url="/admin/projects", status_code=303)


# ===== BLOG POSTS =====
@router.get("/posts")
def admin_posts(request: Request, db: Session = Depends(get_db)):
    require_admin(request, db)
    items = db.query(BlogPost).order_by(BlogPost.id.desc()).all()
    return templates.TemplateResponse(
        "admin/posts.html",
        base_ctx(request, items=items),
    )


@router.get("/posts/new")
def post_new(request: Request, db: Session = Depends(get_db)):
    require_admin(request, db)
    return templates.TemplateResponse(
        "admin/post_form.html",
        base_ctx(request, item=None),
    )


@router.get("/posts/{pid}/edit")
def post_edit(pid: int, request: Request, db: Session = Depends(get_db)):
    require_admin(request, db)
    item = db.query(BlogPost).filter(BlogPost.id == pid).first()
    if not item:
        raise HTTPException(404, "Post no encontrado")
    return templates.TemplateResponse(
        "admin/post_form.html",
        base_ctx(request, item=item),
    )


@router.post("/posts/save")
def post_save(
    request: Request,
    db: Session = Depends(get_db),
    id: str = Form(""),
    title: str = Form(...),
    category: str = Form("Tendencias"),
    author: str = Form("Equipo Aqua-Terra"),
    excerpt: str = Form(""),
    content: str = Form(""),
    cover_image: str = Form(""),
    read_time_min: int = Form(4),
):
    require_admin(request, db)
    if id.strip():
        item = db.query(BlogPost).filter(BlogPost.id == int(id)).first()
        if not item:
            raise HTTPException(404, "Post no encontrado")
    else:
        item = BlogPost(slug=slugify(title), title=title, publish_date=datetime.utcnow())
        db.add(item)
    item.title = title
    item.slug = slugify(title)
    item.category = category
    item.author = author
    item.excerpt = excerpt
    item.content = content
    item.cover_image = cover_image
    item.read_time_min = read_time_min
    db.commit()
    return RedirectResponse(url="/admin/posts", status_code=303)


@router.post("/posts/{pid}/delete")
def post_delete(pid: int, request: Request, db: Session = Depends(get_db)):
    require_admin(request, db)
    item = db.query(BlogPost).filter(BlogPost.id == pid).first()
    if item:
        db.delete(item)
        db.commit()
    return RedirectResponse(url="/admin/posts", status_code=303)


# ===== TESTIMONIALS =====
@router.get("/testimonials")
def admin_testimonials(request: Request, db: Session = Depends(get_db)):
    require_admin(request, db)
    items = db.query(Testimonial).order_by(Testimonial.id.desc()).all()
    return templates.TemplateResponse(
        "admin/testimonials.html",
        base_ctx(request, items=items),
    )


@router.post("/testimonials/save")
def testimonial_save(
    request: Request,
    db: Session = Depends(get_db),
    id: str = Form(""),
    client_name: str = Form(...),
    client_role: str = Form(""),
    company: str = Form(""),
    text: str = Form(""),
    rating: int = Form(5),
    is_featured: str = Form(""),
):
    require_admin(request, db)
    if id.strip():
        item = db.query(Testimonial).filter(Testimonial.id == int(id)).first()
        if not item:
            raise HTTPException(404, "Testimonio no encontrado")
    else:
        item = Testimonial(client_name=client_name)
        db.add(item)
    item.client_name = client_name
    item.client_role = client_role
    item.company = company
    item.text = text
    item.rating = rating
    item.is_featured = (is_featured == "on")
    db.commit()
    return RedirectResponse(url="/admin/testimonials", status_code=303)


@router.post("/testimonials/{tid}/delete")
def testimonial_delete(tid: int, request: Request, db: Session = Depends(get_db)):
    require_admin(request, db)
    item = db.query(Testimonial).filter(Testimonial.id == tid).first()
    if item:
        db.delete(item)
        db.commit()
    return RedirectResponse(url="/admin/testimonials", status_code=303)


# ===== USERS =====
@router.get("/users")
def admin_users(request: Request, db: Session = Depends(get_db)):
    require_admin(request, db)
    items = db.query(User).order_by(User.id.desc()).all()
    return templates.TemplateResponse(
        "admin/users.html",
        base_ctx(request, items=items),
    )


@router.post("/users/{uid}/toggle-admin")
def user_toggle_admin(uid: int, request: Request, db: Session = Depends(get_db)):
    admin = require_admin(request, db)
    if admin.id == uid:
        raise HTTPException(400, "No puedes modificar tu propio rol.")
    item = db.query(User).filter(User.id == uid).first()
    if item:
        item.is_admin = not item.is_admin
        db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)


@router.post("/users/{uid}/toggle-active")
def user_toggle_active(uid: int, request: Request, db: Session = Depends(get_db)):
    admin = require_admin(request, db)
    if admin.id == uid:
        raise HTTPException(400, "No puedes desactivar tu propia cuenta.")
    item = db.query(User).filter(User.id == uid).first()
    if item:
        item.is_active = not item.is_active
        db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)


@router.post("/users/{uid}/delete")
def user_delete(uid: int, request: Request, db: Session = Depends(get_db)):
    admin = require_admin(request, db)
    if admin.id == uid:
        raise HTTPException(400, "No puedes eliminar tu propia cuenta.")
    item = db.query(User).filter(User.id == uid).first()
    if item:
        db.delete(item)
        db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)


@router.post("/users/{uid}/reset-password")
def user_reset_password(
    uid: int, request: Request,
    new_password: str = Form(...),
    db: Session = Depends(get_db),
):
    require_admin(request, db)
    if len(new_password) < 6:
        raise HTTPException(400, "Password muy corto")
    item = db.query(User).filter(User.id == uid).first()
    if item:
        item.password_hash = hash_password(new_password)
        db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)


# ===== SITE CONTENT (texto editable) =====
@router.get("/content")
def admin_content(request: Request, db: Session = Depends(get_db)):
    require_admin(request, db)
    return templates.TemplateResponse(
        "admin/content.html",
        base_ctx(request),
    )


# ===== CONTACT SUBMISSIONS =====
@router.get("/contacts")
def admin_contacts(request: Request, db: Session = Depends(get_db)):
    require_admin(request, db)
    items = db.query(ContactSubmission).order_by(ContactSubmission.id.desc()).all()
    quotes = db.query(QuoteRequest).order_by(QuoteRequest.id.desc()).limit(50).all()
    subs = db.query(NewsletterSubscriber).order_by(NewsletterSubscriber.id.desc()).all()
    return templates.TemplateResponse(
        "admin/contacts.html",
        base_ctx(request, items=items, quotes=quotes, subs=subs),
    )
