# Unit Tests

The unit tests use Python `unittest` and live in `tests/`.

## Recommended: Run Tests In Docker

This avoids installing packages into the host Linux environment.

First build the runtime image:

```bash
docker compose --env-file environments/dev/.env build fortinet_socaas
```

Then run the tests inside the built image:

```bash
docker run --rm -v "$PWD":/work -w /work fortinet-socaas-fortinet_socaas python -m unittest discover -s tests
```

Expected result:

```text
Ran 8 tests

OK
```

## Local Run

Only use this if your local Python environment already has the project dependencies installed.

```bash
python -m unittest discover -s tests
```

## Compile Check

Run this to catch syntax/import issues:

```bash
python -m compileall app.py src tests fortiauth_demo.py syslog_demo.py
```

## What The Tests Cover

- Settings/env parsing.
- `last_run.txt` fallback and existing-state behavior.
- Alert response extraction.
- OAuth token fetch and credential cache persistence.
- Alert request URL and date parameters.

## What The Tests Do Not Cover

- Real Fortinet SOCaaS API.
- Real syslog collector delivery.
- Docker cron scheduling.
- Host permissions for `./state`.

Use the dev integration test in `README.md` for container-level flow validation.
