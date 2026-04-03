# concurrency_lab

Small Django REST API for comparing concurrency strategies against simple CPU-bound and IO-bound workloads.

Available models:
- `thread`
- `process`
- `async`

Core API:
- `POST /api/experiments/` creates an experiment in `pending` state
- `GET /api/experiments/` lists runs
- `GET /api/experiments/<id>/` returns run details and worker results
- `POST /api/experiments/<id>/run/` executes the experiment
