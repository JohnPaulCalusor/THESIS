# DevOps Audit (2025-11-11 17:59:16 UTC)

## OTP limiter configuration
- Location-based limiters live in `/etc/nginx/snippets/otp_email_limit_location.conf`, so every OTP-related ingress request includes that snippet and can surface the `x-otp-limiter` response header for tracing.
- The shared rate zone that backs the snippet is defined in `/etc/nginx/conf.d/otp_ratelimit.conf`; no `papsas-otp.conf` is in use anywhere in the stack.
- `sites-available/papsas.conf` includes the limiter snippet and is symlinked into `sites-enabled/` so the configuration is active.

Decision: `/etc/nginx/snippets/otp_email_limit_location.conf` and `/etc/nginx/conf.d/otp_ratelimit.conf` are the canonical limiter bundle; we no longer use `papsas-otp.conf`.

## How to test as root
- `sudo nginx -t`
- `sudo systemctl reload nginx`
- `curl -I https://api.papsasinc.com/api/auth/email/start` (or the existing smoke endpoints) and confirm `x-otp-limiter: 1` appears in the response headers.
