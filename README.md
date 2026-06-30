# FuelHub Web Scraper

This repository is part of the FuelHub project, a fuel price search and route-based decision support system for Romania.

The scraper is the data entry point of FuelHub. It collects public fuel price data, groups raw rows into station-level records, uploads them to the backend, and triggers the daily statistics recomputation.

## Project Role

- Scrapes Romanian fuel price data from supported providers.
- Converts raw fuel rows into grouped station payloads.
- Uploads station and fuel price batches to the backend API.
- Sends the backend API key through the `X-API-Key` header.
- Can trigger backend statistics recomputation after upload.
- Can run locally, in Docker, or as a Kubernetes CronJob.

## Tech Stack

- Python
- Scrapy
- Requests
- Docker
- Kubernetes CronJob support

## Structure

```text
fuelhub_web_scraper/
  fuelhub_web_scraper/spiders/  Scrapy spiders
  group_fuels.py                Groups raw fuel rows by station
  run_pipeline.py               End-to-end scraper pipeline
requirements.txt                Python dependencies
```

## Local Development

Install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run the full pipeline:

```powershell
Set-Location fuelhub_web_scraper
$env:BACKEND_API_BASE_URL="http://localhost:5200"
$env:BACKEND_API_KEY="your-local-api-key"
python run_pipeline.py
```

## Configuration

Important environment variables:

- `BACKEND_API_BASE_URL` - Backend base URL.
- `BACKEND_API_KEY` - API key sent to protected backend endpoints.
- `SCRAPY_SPIDER` - Spider name, default is `peco`.
- `UPLOAD_BATCH_SIZE` - Number of grouped stations per upload batch.
- `STATS_RECOMPUTE_ENABLED` - Enables statistics recomputation after upload.

## Docker

```powershell
docker build -t fuelhub-web-scraper:latest .
docker run --rm `
  -e BACKEND_API_BASE_URL="http://host.docker.internal:5200" `
  -e BACKEND_API_KEY="your-api-key" `
  fuelhub-web-scraper:latest
```

## FuelHub Repositories

- `fuelhub-backend-v2` - ASP.NET Core backend API
- `fuelhub-frontend` - React and Leaflet frontend
- `fuelhub-web-scraper` - Python Scrapy data pipeline
- `fuelhub-infrastructure` - Terraform and Kubernetes infrastructure
