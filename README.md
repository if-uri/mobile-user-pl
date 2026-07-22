# mobile-user-pl — Jan Kowalski's virtual phone

The **SMS app on the handset** of an average citizen, part of the isolated
digital twin. It shows the inbox from the virtual carrier (the `sms-gateway` in
[net-user-pl](https://github.com/digitaltwin-run/net-user-pl)) — so a human reads the
one-time bank code here, and an automat can read the very same inbox over the
mesh to complete a login exactly as a person would.

Trio: [net-user-pl](https://github.com/digitaltwin-run/net-user-pl) (network) · [pc-user-pl](https://github.com/digitaltwin-run/pc-user-pl) (computer) · **mobile-user-pl** (phone). Orchestrated by [`pc1`](https://github.com/digitaltwin-run/pc1).

## Service

| Service | Role | URI scheme |
| --- | --- | --- |
| `phone` | SMS inbox web app, served as `phone.jan.pl`; JSON inbox for automation | `phone://` |

Endpoints: `/` (big-text inbox UI, auto-refresh), `/api/inbox` (JSON),
`/health`. Owner `jan`, number `+48500100200` (configurable via env).

## Run

Needs net-user-pl up (it creates `netpl` and the SMS gateway):

```bash
docker network create netpl                      # idempotent
docker compose -f compose.mobile.yml up -d
```

Opening the inbox records `phone://jan/sms/query/open`; reading it records
`phone://jan/sms/query/read` on the shared URI event bus.
