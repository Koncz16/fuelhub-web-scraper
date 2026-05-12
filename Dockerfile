FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt

# requirements.txt is UTF-16 in this repository; convert to UTF-8 for pip.
RUN python - <<'PY'
from pathlib import Path

raw = Path('/app/requirements.txt').read_bytes()
text = None
for encoding in ('utf-8-sig', 'utf-16', 'utf-16-le', 'utf-16-be'):
    try:
        text = raw.decode(encoding)
        break
    except UnicodeDecodeError:
        continue

if text is None:
    text = raw.decode('utf-8', errors='ignore')

Path('/tmp/requirements.txt').write_text(text, encoding='utf-8')
PY

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY fuelhub_web_scraper /app/fuelhub_web_scraper

WORKDIR /app/fuelhub_web_scraper

CMD ["python", "run_pipeline.py"]
