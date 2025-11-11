.PHONY: dev-install test

dev-install:
	. .venv/bin/activate && pip install -r requirements-dev.txt

test:
	TMPDIR=/srv/papsas/app/.tmp DJANGO_ENV=dev pytest -q
