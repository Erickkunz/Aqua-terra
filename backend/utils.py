import re
import unicodedata
from typing import Iterable


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)


def best_bulk_discount(qty: int, bulk_discount: dict | None) -> float:
    if not bulk_discount:
        return 0.0
    applicable = [float(rate) for threshold, rate in bulk_discount.items() if qty >= int(threshold)]
    return max(applicable) if applicable else 0.0


def format_currency(value: float, currency: str = "USD") -> str:
    return f"{currency} {value:,.0f}"


def chunked(seq: Iterable, size: int):
    buf = []
    for item in seq:
        buf.append(item)
        if len(buf) == size:
            yield buf
            buf = []
    if buf:
        yield buf
