from pydantic import BaseModel, EmailStr, Field


class ContactIn(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    phone: str = Field(default="", max_length=60)
    inquiry_type: str = Field(default="general", max_length=60)
    pillar: str = Field(default="", max_length=60)
    message: str = Field(min_length=5, max_length=4000)


class QuoteItem(BaseModel):
    product_id: int
    qty: int = Field(ge=1, le=10000)


class QuoteIn(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    company: str = Field(default="", max_length=200)
    phone: str = Field(default="", max_length=60)
    country: str = Field(default="", max_length=80)
    items: list[QuoteItem]
    notes: str = Field(default="", max_length=2000)


class NewsletterIn(BaseModel):
    email: EmailStr
    source: str = Field(default="footer", max_length=60)


class CartItemIn(BaseModel):
    product_id: int
    qty: int = Field(ge=1, le=10000, default=1)
