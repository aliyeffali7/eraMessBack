import logging
import os

import firebase_admin
from django.conf import settings
from firebase_admin import credentials, messaging

from .models import PushToken

logger = logging.getLogger(__name__)

_firebase_app = None
_firebase_init_failed = False


def _get_firebase_app():
    global _firebase_app, _firebase_init_failed
    if _firebase_app is not None or _firebase_init_failed:
        return _firebase_app
    path = str(settings.FIREBASE_CREDENTIALS_PATH)
    if not os.path.exists(path):
        logger.warning("Firebase credentials not found at %s; push notifications disabled.", path)
        _firebase_init_failed = True
        return None
    try:
        cred = credentials.Certificate(path)
        _firebase_app = firebase_admin.initialize_app(cred)
    except Exception:
        logger.exception("Failed to initialize Firebase app.")
        _firebase_init_failed = True
        return None
    return _firebase_app


def register_token(*, user, token: str):
    PushToken.objects.update_or_create(token=token, defaults={"user": user})


def send_push_to_users(*, user_ids, title: str, body: str, data: dict | None = None):
    app = _get_firebase_app()
    if app is None:
        return
    tokens = list(PushToken.objects.filter(user_id__in=user_ids).values_list("token", flat=True))
    if not tokens:
        return
    message = messaging.MulticastMessage(
        notification=messaging.Notification(title=title, body=body),
        data={k: str(v) for k, v in (data or {}).items()},
        tokens=tokens,
    )
    try:
        response = messaging.send_each_for_multicast(message, app=app)
        if response.failure_count:
            for idx, res in enumerate(response.responses):
                if not res.success:
                    logger.warning("Push failed for token %s...: %s", tokens[idx][:20], res.exception)
        logger.info("Push sent: %s success, %s failure", response.success_count, response.failure_count)
    except Exception:
        logger.exception("Push send raised an exception.")
