from datetime import datetime
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    icon: Mapped[str] = mapped_column(String(60), default="droplet")

    products: Mapped[list["Product"]] = relationship(back_populates="category", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    short_description: Mapped[str] = mapped_column(String(280), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    price: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(6), default="USD")
    image_url: Mapped[str] = mapped_column(String(400), default="")
    in_stock: Mapped[bool] = mapped_column(Boolean, default=True)
    stock_qty: Mapped[int] = mapped_column(Integer, default=10)
    rating: Mapped[float] = mapped_column(Float, default=5.0)
    reviews_count: Mapped[int] = mapped_column(Integer, default=0)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    specifications: Mapped[dict] = mapped_column(JSON, default=dict)
    features: Mapped[list] = mapped_column(JSON, default=list)
    bulk_discount: Mapped[dict] = mapped_column(JSON, default=dict)  # { "10": 0.05, "50": 0.12 }
    tech_tags: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    category: Mapped[Category] = relationship(back_populates="products")
    reviews: Mapped[list["ProductReview"]] = relationship(back_populates="product", cascade="all, delete-orphan")


class ProductReview(Base):
    __tablename__ = "product_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    author: Mapped[str] = mapped_column(String(120), default="Anonimo")
    rating: Mapped[int] = mapped_column(Integer, default=5)
    text: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    product: Mapped[Product] = relationship(back_populates="reviews")
