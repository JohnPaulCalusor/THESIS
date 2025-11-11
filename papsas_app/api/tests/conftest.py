import pytest
from django.core.cache import cache

@pytest.fixture(autouse=True)
def no_ssl_and_fresh_cache(settings):
    """
    Disable HTTPS redirection in tests and keep throttle cache clean so
    per-test DRF throttles don't bleed between cases.
    """
    settings.SECURE_SSL_REDIRECT = False
    settings.SESSION_COOKIE_SECURE = False
    settings.CSRF_COOKIE_SECURE = False
    cache.clear()
    try:
        yield
    finally:
        cache.clear()
