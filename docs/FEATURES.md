# Features

Headline-feature inventory for `eco-jobs-tracker`. Baseline for scope-change evaluation. "What does this repo do," not file-level detail.

## Shape

Two-process system: a C# Eco server mod exposing a read-only HTTP endpoint of every player's learned specialties, and a FastAPI dashboard rendering it as a "who can make what" board.

## Web dashboard (FastAPI)

- **Live HTML dashboard at `eco-jobs-tracker.coilysiren.me`** - Stacked sections for Professions, Specialties, Players. Tailwind CDN, no build step.
- **Drill-down pages** - `/professions`, `/specialties`, `/players` each render one section without the eco-card header, for direct linking.
- **Embedded live server-status card** - Top of homepage embeds the same card rendered by sibling `eco-mcp-app` (git dep). Stays in lockstep with the MCP widget.
- **HTMX partials** - `/partials/eco-card` and `/partials/profession/{name}` serve fragments for in-page expansion.
- **JSON API mirror** - `/api/v1/professions`, `/api/v1/players`, `/api/v1/specialties` return same data, machine-readable.
- **Iframe embedding** - CSP `frame-ancestors` allows `coilysiren.me` to embed (eco-modding page on personal site).
- **Healthcheck** - `/healthz` returns `{"ok": true}` for k8s probes.
- **Mock-data fallback** - `UPSTREAM_URL` unset = serves canned data from `mock_data.py`. UI flags via `using_mock_data` template global.
- **Upstream mod fetch** - `UPSTREAM_URL` set = `upstream.py` calls `/api/v1/skills`, forwards `UPSTREAM_API_KEY` as `X-API-Key`, 5s timeout. No fallback on dead endpoint (intentional).
- **Dev-only livereload** - `DEBUG`-gated `/ws/livereload` WebSocket + injected script. CSS swaps without full reload. Zero prod cost.
- **Sentry telemetry** - `SENTRY_DSN`-gated init. No-op when unset.

## C# Eco mod (`EcoJobsTracker.dll`)

- **`GET /api/v1/skills` endpoint** - Standard ModKit UserCode mod, `[ApiController]` picked up by Eco's ASP.NET host.
- **Every player's learned specialties** - Iterates `UserManager.Users`, filters skills `Level > 0 && IsSpecialty`, returns name/level/max-level + online state.
- **Auth via Eco's admin-token middleware** - Same `X-API-Key` gate as the rest of `/api/v1/*`. No bespoke auth.
- **Dual-attribute DTOs** - Records carry both `System.Text.Json` and `Newtonsoft.Json` camelCase attributes so they serialize identically under either pipeline.
- **mod.io distribution** - Listing copy + zip-shape in `docs/modio.md`.

## Shell harness (`mod/shell/`)

- **Standalone ASP.NET mock on `:5100`** - Same route, same DTOs (`<Compile Include>`-linked), canned data. Iterate without booting Eco.

## Deploy and ops

- **Canonical deploy reference for the homelab** - Other `coilysiren/*` repos copy from here. Dockerfile, Makefile, `deploy/main.yml`, GHA pipeline.
- **k3s + ExternalSecrets** - Pulls `SENTRY_DSN` + `UPSTREAM_API_KEY` from AWS SSM via `aws-parameter-store` ClusterSecretStore.
- **Image publish** - Builds + pushes to `ghcr.io/coilysiren/eco-spec-tracker/...`, git-SHA tagged.
- **Tailscale + Traefik + cert-manager** - Inherited from `backend` template.
- **`coily eco mod push` path** - `make build-mod`, zip with `Mods/EcoJobsTracker/` prefix, push via coily, `coily eco restart`.

## Dev-loop tooling

- **`make build-native` / `run-native`** - `uv sync --group dev`, uvicorn `--reload` on `:4100`.
- **`make run-shell`** - C# shell harness on `:5100`.
- **`make build-mod`** - Production mod DLL.
- **`make build-docker` / `deploy`** - Container build/push + k3s rollout.
- **Pre-commit** - ruff + mypy on Python, `dotnet format` on C#.
- **Smoke suite** - `tests/test_smoke.py` every page, every JSON, eco-card partial (upstream `/info` stubbed via respx), upstream parser fixture.

## Naming-debt note

Public: `eco-jobs-tracker` (repo, subdomain, mod). Internal still uses older `eco-spec-tracker` (k8s namespace, package, image, SSM key, Sentry). Renaming internals is deferred.

## See also

- [README.md](../README.md) - human-facing intro.
- [AGENTS.md](../AGENTS.md) - agent-facing operating rules.
- [.coily/coily.yaml](../.coily/coily.yaml) - allowlisted commands.

Cross-reference convention from [coilysiren/agentic-os#59](https://github.com/coilysiren/agentic-os/issues/59).
