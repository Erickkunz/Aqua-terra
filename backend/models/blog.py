from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class BlogPost(Base):
    __tablename__ = "blog_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(220), nullable=False)
    excerpt: Mapped[str] = mapped_column(String(400), default="")
    content: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(80), default="Tendencias")
    author: Mapped[str] = mapped_column(String(160), default="Equipo Aqua-Terra")
    cover_image: Mapped[str] = mapped_column(String(400), default="")
    read_time_min: Mapped[int] = mapped_column(Integer, default=4)
    publish_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
