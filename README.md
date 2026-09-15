# Multi-Tenant Job Queue and Analytics API with Role-Based Access Control
Educational starter using FastAPI, Celery, Redis, PostgreSQL, JWT and Docker.

## Run
Copy `.env.example` to `.env`; run `docker compose up --build`; open http://localhost:8000/docs.
In development, use POST `/dev/token` to get a demo token. Upload a CSV to POST `/jobs` with a Bearer token and `Idempotency-Key` header, then poll GET `/jobs/{job_id}`.

Worker lifecycle: queued -> running -> completed/failed. The worker computes row count, columns, missing values and duplicate rows. `tenant_id` filters isolate tenant data.

This scaffold does not prove 1.1M rows were processed or that 94s -> 31s / p95 380ms was measured. Run your own reproducible benchmark before using those claims.
