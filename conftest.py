import pytest
from uuid import uuid4
from django.core.cache import cache
from django.contrib.auth import get_user_model

@pytest.fixture(autouse=True)
def _test_http_and_cache(settings):
    """
    Test-only: avoid HTTPS 301s and throttle/cache bleed between tests.
    """
    settings.SECURE_SSL_REDIRECT = False
    settings.SESSION_COOKIE_SECURE = False
    settings.CSRF_COOKIE_SECURE = False
    cache.clear()
    try:
        yield
    finally:
        cache.clear()

@pytest.fixture(autouse=True)
def _auto_unique_email(monkeypatch):
    """
    Test-only: make sure empty emails stay unique so legacy tests do not fail.
    """
    User = get_user_model()
    ManagerCls = User.objects.__class__
    original = ManagerCls.create_user

    def create_user_proxy(self, username, email=None, password=None, **extra):
        if not email:
            email = f"auto+{uuid4().hex[:8]}@test.local"
        return original(self, username, email, password, **extra)

    monkeypatch.setattr(ManagerCls, "create_user", create_user_proxy)
