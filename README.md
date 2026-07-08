# Fortinet SOCaaS Alert Forwarder

One-shot Docker job that collects Fortinet SOCaaS alerts since the previous successful run and forwards them to a syslog collector.

## Runtime Model

The container is created once and started by the host scheduler every 5 minutes:

```bash
# For required env variables
docker compose --env-file environments/prod/.${CUSTOMER_ID}_env up --no-start --build --force-recreate fortinet_socaas
```

Cron example with overlap protection:

```cron
*/5 * * * * flock -n /tmp/fortinet_socaas.lock -c 'cd /path/to/FortiNet-SOCaaS && docker start fortinet_socaas >/dev/null 2>&1'
```

The job exits after one collection cycle:

- `0`: API request, syslog forwarding, and `last_run` update completed.
- `1`: startup validation, auth, API, syslog, or state update failed.

## Required Environment

Provide these variables through a Compose env file or the runtime environment:

```env
CUSTOMER_ID=
COLLECTOR_IP=
COLLECTOR_PORT=
FORTICLOUD_AUTH_URL=
FORTINET_SOCAAS_URL=
FORTINET_SOCAAS_API_ID=
FORTINET_SOCAAS_PASSWORD=
FORTINET_SOCAAS_CLIENT_ID=
```

Production defaults to HTTPS-only for `FORTINET_SOCAAS_URL`. The optional `FORTINET_SOCAAS_ALLOW_INSECURE_HTTP=true` flag is intended only for local/dev test services.

## State

Runtime state is persisted at `/app/state`, mounted from `./state/${CUSTOMER_ID}` by Compose:

- `creds.json`: OAuth token cache.
- `last_run.txt`: end timestamp from the last successful run.

`last_run.txt` is updated only after the alert API request and syslog forwarding complete successfully. If a run fails, the next run retries the same window.

## Operations

Create or recreate the stopped job container after code or environment changes:

```bash
docker compose --env-file environments/prod/.${CUSTOMER_ID}_env up --no-start --build --force-recreate fortinet_socaas
```

Start one run manually:

```bash
docker start fortinet_socaas
```

Inspect logs and exit status:

```bash
docker logs fortinet_socaas
docker inspect fortinet_socaas --format '{{.State.ExitCode}}'
```

Check persisted state:

```bash
ls -l state/${CUSTOMER_ID}
cat state/${CUSTOMER_ID}/last_run.txt
```

## Development Integration Test

The dev env starts a fake Fortinet API and a UDP syslog receiver:

```bash
docker compose --env-file environments/dev/.env up --build -d --force-recreate fortiauth_demo syslog_demo
docker compose --env-file environments/dev/.env up --no-start --build --force-recreate fortinet_socaas
docker start fortinet_socaas
docker wait fortinet_socaas
```

Verify:

```bash
docker logs ${CUSTOMER_ID}_fortinet_socaas
docker logs fortiauth_demo
docker logs syslog_demo
docker inspect ${CUSTOMER_ID}_fortinet_socaas --format '{{.State.ExitCode}}'
```

Expected evidence:

- `fortinet_socaas` exits `0`.
- `fortiauth_demo` logs an `/alert` request with `created_date_from` and `created_date_to`.
- `syslog_demo` logs the forwarded alert JSON.
- `state/creds.json` and `state/last_run.txt` exist.

## Tests

Run unit tests in a disposable Python container so the host Python environment is not modified:

```bash
docker run --rm -v "$PWD":/work -w /work python:3.10.12-alpine sh -c "pip install --no-cache-dir -r requirements.txt >/dev/null && python -m unittest discover -s tests"
```

## Production Notes

- Keep `.env` and `state/` out of Git.
- Restrict permissions on the env file and `state/` directory.
- Keep `FORTINET_SOCAAS_ALLOW_INSECURE_HTTP` unset or `false` in production.
- Verify syslog delivery against the real collector before enabling cron.
- Keep the `flock` wrapper in cron to prevent overlapping runs.
