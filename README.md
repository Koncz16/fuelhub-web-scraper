# FuelHub Scraper

This repository contains a Python-based web scraper that collects real-time fuel price data from various sources.

## Features
- Scrapes fuel price information from supported websites
- Stores collected data in a structured format for further processing

## Technologies
- Python
- Srcapy

## Automated Pipeline
The project now supports an end-to-end execution flow:
1. Run Scrapy spider and save a raw file.
2. Group station prices by station into one grouped file.
3. Upload grouped data to the backend batch endpoint.
4. Trigger backend statistics recompute for the uploaded date or date range.

The orchestrator script is `fuelhub_web_scraper/run_pipeline.py`.

### Environment Variables
- `BACKEND_API_BASE_URL` (required): Backend base URL.
- `FUEL_BATCH_ENDPOINT` (optional, default `/api/fuel/batch`): Upload endpoint path.
- `BACKEND_API_KEY` (required): API key for backend authentication (sent as X-API-Key header).
- `SCRAPY_SPIDER` (optional, default `peco`): Spider name to execute.
- `RAW_FILENAME` (optional): Override generated raw output filename.
- `UPLOAD_BATCH_SIZE` (optional, default `300`): Items per POST request.
- `UPLOAD_TIMEOUT_SECONDS` (optional, default `30`): Request timeout in seconds.
- `UPLOAD_MAX_RETRIES` (optional, default `3`): Retries per batch.
- `UPLOAD_RETRY_BACKOFF_SECONDS` (optional, default `2`): Backoff multiplier.
- `STATS_RECOMPUTE_ENABLED` (optional, default `true`): Enable/disable post-upload stats recompute call.
- `STATS_RECOMPUTE_ENDPOINT` (optional, default `/api/statistics/recompute`): Recompute endpoint path.
- `STATS_RECOMPUTE_TIMEOUT_SECONDS` (optional, default uses `UPLOAD_TIMEOUT_SECONDS`): Recompute request timeout in seconds.
- `STATS_RECOMPUTE_MAX_RETRIES` (optional, default uses `UPLOAD_MAX_RETRIES`): Retries for recompute call.
- `STATS_RECOMPUTE_RETRY_BACKOFF_SECONDS` (optional, default uses `UPLOAD_RETRY_BACKOFF_SECONDS`): Backoff multiplier for recompute call.

### Run Locally
From repository root:

```powershell
Set-Location fuelhub_web_scraper
$env:BACKEND_API_BASE_URL="http://localhost:8080"
python run_pipeline.py
```

## Docker
Build and run from repository root:

```powershell
docker build -t fuelhub-web-scraper:latest .
docker run --rm \
	-e BACKEND_API_BASE_URL="http://host.docker.internal:8080" \
	-e BACKEND_API_TOKEN="your-token" \
	fuelhub-web-scraper:latest
```

## Kubernetes CronJob
The `k8s` folder includes manifests for a scheduled run:
- `k8s/configmap.yaml`
- `k8s/secret.example.yaml`
- `k8s/cronjob.yaml`

### Deploy
1. Build and push image, then update image in `k8s/cronjob.yaml`.
2. Create secret file from example and set the real token.
3. Apply manifests:

```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.example.yaml
kubectl apply -f k8s/cronjob.yaml
```

### Trigger Manual Test Job

```bash
kubectl create job --from=cronjob/fuelhub-scraper fuelhub-scraper-manual-001
kubectl logs job/fuelhub-scraper-manual-001 -f
```
