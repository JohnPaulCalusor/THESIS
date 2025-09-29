# papsas_app/utils/otp_throttle.py
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

def _key(prefix, user_id): return f"otp:{prefix}:{user_id}"

def can_send_otp(user_id, max_per_window, window_minutes):
    now = timezone.now()
    window_key = _key("send_window", user_id)
    count_key = _key("send_count", user_id)

    if cache.get(window_key) is None:
        cache.set(window_key, 1, timeout=window_minutes*60)
        cache.set(count_key, 1, timeout=window_minutes*60)
        return True, 0

    count = cache.incr(count_key)
    remaining = max(0, max_per_window - count)
    return (count <= max_per_window, remaining)

def too_many_verify_attempts(user_id, lock_minutes):
    lock_key = _key("verify_lock", user_id)
    return cache.get(lock_key) is not None

def register_verify_failure(user_id, max_attempts, lock_minutes):
    attempts_key = _key("verify_attempts", user_id)
    attempts = cache.get(attempts_key, 0) + 1
    cache.set(attempts_key, attempts, timeout=lock_minutes*60)
    if attempts >= max_attempts:
        cache.set(_key("verify_lock", user_id), 1, timeout=lock_minutes*60)
        return True
    return False

def reset_verify_window(user_id):
    cache.delete_many([_key("verify_attempts", user_id), _key("verify_lock", user_id)])
