import os

from .base import *  # noqa: F401,F403

DEBUG = False

ALLOWED_HOSTS = [h for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h]

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

CORS_ALLOWED_ORIGINS = [o for o in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",") if o]
