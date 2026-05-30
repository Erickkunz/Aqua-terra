"""Shared rate limiter (slowapi).

In-memory storage by default (per-process). For multi-worker production,
point STORAGE_URI to Redis, e.g. redis://localhost:6379.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
