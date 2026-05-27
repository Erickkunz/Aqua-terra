"""Order + OrderItem models for the shop checkout flow (WebPay)."""
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    # Buyer info (snapshot - works for guest checkout too)
    buyer_name: Mapped[str] = mapped_column(String(160), default="")
    buyer_email: Mapped[str] = mapped_column(String(160), default="")
    buyer_phone: Mapped[str] = mapped_column(String(60), default="")
    buyer_address: Mapped[str] = mapped_column(String(400), default="")

    # Money
    subtotal: Mapped[float] = mapped_column(Float, default=0.0)
    total: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(8), default="CLP")

    # WebPay flow
    buy_order: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    session_id: Mapped[str] = mapped_column(String(80), default="")
    webpay_token: Mapped[str] = mapped_column(String(120), default="", index=True)
    webpay_authorization_code: Mapped[str] = mapped_column(String(40), default="")
    webpay_payment_type: Mapped[str] = mapped_column(String(40), default="")
    webpay_response_code: Mapped[int] = mapped_column(Integer, nullable=True)
    webpay_card_last4: Mapped[str] = mapped_column(String(8), default="")

    # Snapshot of cart at checkout (list of {product_id, name, qty, price})
    items_snapshot: Mapped[list] = mapped_column(JSON, default=list)

    # State machine: pending | paid | failed | aborted
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    paid_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
