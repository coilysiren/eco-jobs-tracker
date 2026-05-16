# Agent instructions

See `../AGENTS.md` for workspace conventions. This file covers what's specific.

---

# eco-spec-tracker / eco-jobs-tracker

FastAPI + Jinja2 + HTMX app listing every Eco player's jobs (professions/specialties) with `active / total` counts. Paired with a C# Eco mod exposing `/api/v1/skills`. Deploy: `eco-jobs-tracker.coilysiren.me` (k3s homelab).

## Deploy reference

This repo is the **canonical reference** for the current deploy shape - other repos copy from here (commit `49f99e4`). Comprehensive writeup at [`infrastructure/docs/k3s-deploy-notes.md`](../infrastructure/docs/k3s-deploy-notes.md). Read before touching Dockerfile, Makefile, `deploy/main.yml`, GHA, or Tailscale/k3s secrets. Add new pitfalls to its §7 / §9.

## Project layout

Python (web app):
- `src/eco_spec_tracker/main.py` - FastAPI app. Routes: `/`, `/players`, `/healthz`, `/partials/*`, `/api/v1/*`.
- `src/eco_spec_tracker/mock_data.py` - placeholder matching mod's shape.
- `src/eco_spec_tracker/templates/` - Jinja2. `base.html` layout, `_*.html` HTMX partials. Tailwind CDN.

C# (mod):
- `mod/eco-jobs-tracker.sln` - one solution, two projects.
- `mod/src/EcoJobsTracker.csproj` + `.cs` - the real mod. References `Eco.ReferenceAssemblies`. Drops into `Server/Mods/EcoJobsTracker/`.
- `mod/shell/EcoJobsTracker.Shell.csproj` + `.cs` - standalone ASP.NET harness on `:5100`. Same route, canned data.
- `mod/src/Dtos.cs` - shared DTO records, `<Compile Include>`-linked into the shell.

Deploy rig (cloned from `coilysiren/backend`):
- `Makefile`, `Dockerfile`, `config.yml`, `deploy/main.yml`, `.github/workflows/build-and-publish.yml`.

## Dev loop

- `make build-native` - `uv sync --group dev`.
- `make run-native` - uvicorn `:4100` with `--reload`.
- `make run-shell` - C# harness on `:5100`.
- `make build-mod` - compile real mod DLL.
- `make build-docker` / `make deploy` - build/push image, k3s rollout.
- `pre-commit install` - ruff + mypy + `dotnet format`.

## Data flow

```
Eco server ──[EcoJobsTracker.dll]──► GET /api/v1/skills
                                          ▲
                              or locally  │
                                          │
mod/shell (Shell) ───────────────────────┘  (:5100, mock data)

                FastAPI tracker (:4100 local, eco-jobs-tracker.coilysiren.me)
                    ├─ HTML UI (Jinja2 + HTMX + Tailwind)
                    └─ /api/v1/{professions,players}
```

`UPSTREAM_URL` env var controls whether FastAPI reads `mock_data.py` directly or pulls from shell/mod.

## Eco mod notes

Standard UserCode mod: `.cs` files in `Mods/UserCode/` compile at server boot. Uses public ModKit API (`Eco.ReferenceAssemblies` NuGet, same as `eco-mods-public`).

References:
- Sibling `eco-mods-public` for UserCode layout + `Register.cs`.
- ModKit: https://github.com/StrangeLoopGames/EcoModKit.
- Eco docs: https://docs.play.eco/.

Community `eco-price-calculator` (mod.io) is a known example of HTTP-endpoint mods; source isn't published but confirms approach is standard.

**Do not copy from local Eco source checkout.** Only public ModKit API.

## Sibling repos

- `backend` (public) - canonical deploy template (k3s + GHCR + Tailscale + cert-manager).
- `eco-mcp-app` (public) - MCP server exposing Eco `/info`. Same deploy rig.
- `eco-mods` / `eco-mods-public` (private/public) - C# mods.
- `infrastructure` (public) - k3s, Traefik, cert-manager.
- `kai-server` (public) - homelab k3s box.

## Reaching the homelab

`tailscale up && ssh kai@kai-server`. The GHA `deploy` job does the same (tailscale up → kubeconfig → `make .deploy`).

### Pushing the mod DLL

`coily eco mod push --src EcoJobsTracker.zip`. Zip must contain `Mods/EcoJobsTracker/EcoJobsTracker.dll` (+ sibling `.deps.json` / `.pdb`) so it extracts under `/home/kai/Steam/steamapps/common/EcoServer/`. Then `coily eco restart`. See [`infrastructure/eco.md`](../infrastructure/eco.md) §4 for sequencing (push mod before web picks up `UPSTREAM_URL` - no fallback on dead endpoint).

## Post-push follow-up

After pushing `main`, schedule a wake-up to verify deploy.

- **Cadence**: 720s.
- **Verify CI**: `coily gh run list --repo coilysiren/eco-jobs-tracker --limit 1`. Re-schedule once at +300s if in progress; surface and stop on failure.
- **Verify rollout**: `coily kubectl --context=kai-server -n coilysiren-eco-spec-tracker rollout status deployment/coilysiren-eco-spec-tracker-app --timeout=2m`.
- **Skip** for docs-only pushes.

## See also

- [README.md](README.md) - human-facing intro.
- [docs/FEATURES.md](docs/FEATURES.md) - inventory of what ships today.
- [.coily/coily.yaml](.coily/coily.yaml) - allowlisted commands.

Cross-reference convention from [coilysiren/agentic-os#59](https://github.com/coilysiren/agentic-os/issues/59).
