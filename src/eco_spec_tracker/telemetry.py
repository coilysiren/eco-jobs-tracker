"""Sentry SDK init for eco-spec-tracker.

Mirrors the pattern in `coilysiren/backend/backend/telemetry.py`. When
SENTRY_DSN is set (production, injected via deploy/main.yml's ExternalSecret
sync from SSM /sentry-dsn/eco-spec-tracker), initialize the real client with
Starlette + FastAPI integrations. Otherwise call `sentry_sdk.init()` with no
args, which leaves the SDK in a no-op state so local runs don't ship events.
"""

from __future__ import annotations

import os

import sentry_sdk
import sentry_sdk.integrations.fastapi as sentry_fastapi
import sentry_sdk.integrations.starlette as sentry_starlette


def init_sentry() -> None:
    dsn = os.getenv("SENTRY_DSN")
    if dsn:
        sentry_sdk.init(
            dsn=dsn,
            integrations=[
                sentry_starlette.StarletteIntegration(),
                sentry_fastapi.FastApiIntegration(),
            ],
        )
    else:
        sentry_sdk.init()
