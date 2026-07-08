# Production Readiness Checklist

Use this checklist before enabling the cron schedule in production.

## Configuration

- Confirm production `.env` or runtime environment contains:
  - `COLLECTOR_IP`
  - `COLLECTOR_PORT`
  - `FORTICLOUD_AUTH_URL`
  - `FORTINET_SOCAAS_URL`
  - `FORTINET_SOCAAS_API_ID`
  - `FORTINET_SOCAAS_PASSWORD`
  - `FORTINET_SOCAAS_CLIENT_ID`
- Confirm `FORTINET_SOCAAS_ALLOW_INSECURE_HTTP` is unset or `false`.
- Confirm `FORTINET_SOCAAS_URL` uses HTTPS.
- Confirm the env file is not committed to Git.
- Confirm the env file has restrictive host permissions.

## State

- Confirm `./state` exists on the host.
- Confirm `./state` is writable by the container user.
- Confirm `./state` is not committed to Git.
- Confirm `state/creds.json` and `state/last_run.txt` are protected from unauthorized reads.
- Confirm backups or recovery expectations for `last_run.txt`.

## Container

- Build and recreate the stopped job container:

```bash
docker compose up --no-start --build --force-recreate fortinet_socaas
```

- Confirm the container exists:

```bash
docker ps -a --filter name=fortinet_socaas
```

- Run one manual production test:

```bash
docker start fortinet_socaas
docker wait fortinet_socaas
docker inspect fortinet_socaas --format '{{.State.ExitCode}}'
docker logs fortinet_socaas
```

- Confirm exit code is `0`.
- Confirm logs show the expected collection window.
- Confirm `state/last_run.txt` updates only after a successful run.

## Fortinet API

- Confirm OAuth succeeds with real credentials.
- Confirm `/alert` receives `created_date_from` and `created_date_to`.
- Confirm the returned alert shape matches what the app forwards.
- Confirm API failures exit non-zero and do not advance `last_run.txt`.

## Syslog

- Confirm the real collector receives forwarded alerts.
- Confirm collector timestamp, source, facility, and message format are acceptable.
- Confirm firewall/routing allows UDP syslog from the Docker host/container path.
- Confirm failed collector delivery behavior is acceptable for your syslog transport.

## Scheduling

- Use cron with `flock` to prevent overlapping runs:

```cron
*/5 * * * * flock -n /tmp/fortinet_socaas.lock -c 'cd /path/to/FortiNet-SOCaaS && docker start fortinet_socaas >/dev/null 2>&1'
```

- Confirm cron runs as a user allowed to access Docker.
- Confirm the working directory path is correct.
- Confirm the job finishes in less than 5 minutes during normal operation.

## Monitoring

- Monitor non-zero container exit codes.
- Monitor stale `state/last_run.txt`.
- Monitor Docker log growth and retention.
- Confirm operational ownership for failed runs.

## Rollback

- Keep the previous image or Git revision available.
- Know how to stop cron.
- Know how to recreate the container after config/code changes:

```bash
docker compose up --no-start --build --force-recreate fortinet_socaas
```
