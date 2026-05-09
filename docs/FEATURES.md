# Features

Headline-feature inventory for `eco-jobs-tracker`. Use this as the baseline for evaluating scope changes (additions, removals, drift) over time. Granularity is "what does this repo do for a user / operator," not file-level detail.

Last refreshed: 2026-05-08.

## Shape in one line

A two-process system: a C# Eco server mod that exposes a read-only HTTP endpoint listing every player's learned specialties, and a FastAPI web dashboard that renders that data as a "who can make what" board.

## Headline features

### Web dashboard (FastAPI app)

- **Live HTML dashboard at `eco-jobs-tracker.coilysiren.me`** - Single-page-style site with stacked sections for Professions, Specialties, and Players. Tailwind Play CDN, no build step.
- **Three drill-down pages** - `/professions`, `/specialties`, `/players` each render just one section without the eco-card header, for direct linking.
- **Embedded live Eco server status card** - Top of the homepage embeds the same status card rendered by the sister `eco-mcp-app` package (imported as a git dep). Visuals stay in lockstep with the MCP widget.
- **HTMX partials for in-page expansion** - `/partials/eco-card` and `/partials/profession/{name}` serve fragment HTML for HTMX swaps (e.g. expand a profession to see its players).
- **JSON API mirror** - `/api/v1/professions`, `/api/v1/players`, `/api/v1/specialties` return the same data the HTML pages render, machine-readable.
- **Iframe embedding allowance** - CSP `frame-ancestors` allows `coilysiren.me` to embed the app (the eco-modding page on the personal site).
- **Healthcheck** - `/healthz` returns `{"ok": true}` for k8s probes.
- **Mock-data fallback** - When `UPSTREAM_URL` is unset, the app serves canned data from `mock_data.py` so local dev and offline browsing always work. UI flags this state via a `using_mock_data` template global.
- **Upstream mod fetch** - When `UPSTREAM_URL` is set, `upstream.py` calls the mod's `/api/v1/skills`, optionally forwarding `UPSTREAM_API_KEY` as `X-API-Key`, with a 5s timeout. No fallback on a dead endpoint (intentional, per AGENTS.md sequencing rules).
- **Dev-only browser livereload** - Gated on `DEBUG` env var. Adds a `/ws/livereload` WebSocket and an injected `<script>` so file changes trigger a browser reload (CSS swaps without full reload). Zero runtime cost in prod.
- **Sentry telemetry** - `SENTRY_DSN`-gated init with Starlette + FastAPI + logging integrations. No-op when DSN is unset.

### C# Eco mod (`EcoJobsTracker.dll`)

- **`GET /api/v1/skills` endpoint inside the Eco server process** - Standard ModKit UserCode mod, registered as an `[ApiController]` picked up by Eco's ASP.NET Core host.
- **Returns every player's learned specialties** - Iterates `UserManager.Users`, filters skills with `Level > 0 && IsSpecialty`, returns name, level, max-level, plus the player's online state (`active`).
- **Auth via Eco's admin-token middleware** - Same `X-API-Key` gate the rest of `/api/v1/*` uses. No bespoke auth.
- **Dual-attribute DTOs** - Response records carry both `System.Text.Json` and `Newtonsoft.Json` camelCase attributes so they serialize identically under either pipeline (Eco's vs the shell harness).
- **mod.io distribution** - Listing copy and zip-shape conventions documented in `docs/modio.md`. Publishable as `Eco Jobs Tracker` under the `Script` tag.

### Shell harness (`mod/shell/`)

- **Standalone ASP.NET Core mock server on `:5100`** - Same route, same DTOs (linked via `<Compile Include>`), canned data. Lets the Python app iterate against a real C# HTTP server without booting Eco.

### Deploy and ops

- **Canonical deploy reference for the homelab** - This repo is the reference shape other `coilysiren/*` repos copy from. Dockerfile, Makefile, `deploy/main.yml` (k3s), `.github/workflows/build-and-publish.yml` GHA pipeline.
- **k3s manifest with ExternalSecrets** - Pulls `SENTRY_DSN` and `UPSTREAM_API_KEY` from AWS SSM via the `aws-parameter-store` ClusterSecretStore.
- **Image publish** - Builds and pushes to `ghcr.io/coilysiren/eco-spec-tracker/...`, tagged with git SHA.
- **Tailscale + Traefik + cert-manager rig** - Inherited from the `backend` template. TLS, ingress, and homelab access shape.
- **`coily eco mod push` distribution path** - Mod DLL is built locally with `make build-mod`, zipped with `Mods/EcoJobsTracker/` prefix, pushed via the coily wrapper, then `coily eco restart` reloads it.

### Dev-loop tooling

- **`make build-native` / `make run-native`** - `uv sync --group dev` and uvicorn `--reload` on `:4100`.
- **`make run-shell`** - C# shell harness on `:5100`.
- **`make build-mod`** - Compiles the production mod DLL.
- **`make build-docker` / `make deploy`** - Container build/push and k3s rollout.
- **Pre-commit** - ruff + mypy on Python, `dotnet format` on C#.
- **Smoke test suite** - `tests/test_smoke.py` exercises every page, every JSON endpoint, the eco-card partial (with the upstream Eco `/info` stubbed via respx), and the upstream parser against a mod-shaped fixture. Run via `inv test` or `uv run pytest`.

## Naming-debt note

Public surface: `eco-jobs-tracker` (GitHub repo, subdomain, C# mod). Internal surface still uses the older `eco-spec-tracker` name (k8s namespace, Python package, Docker image, SSM key, Sentry project). Renaming the internals is a separate, riskier surgery and is intentionally deferred.

## Known open questions

- API-key provisioning shape if the mod ever needs its own token instead of reusing the `eco-mcp-app` admin token.
- Whether `active` means "online right now" (current behavior, from `user.LoggedIn`) or "logged in within N days" (mock-era boolean).
