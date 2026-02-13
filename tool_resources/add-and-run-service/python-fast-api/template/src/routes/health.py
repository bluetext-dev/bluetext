import sys
import time
from typing import Any, Optional

from fastapi import APIRouter, Query, Request

import conf
from utils import log
from utils.version import get_app_version

logger = log.get_logger(__name__)

health_router = APIRouter(tags=["health"])

_EXCLUDED_CLIENTS = {"auth"}


def _discover_clients(app) -> dict[str, Any]:
    """Find all *_client attributes on app.state."""
    clients = {}
    for attr_name, value in app.state._state.items():
        if attr_name.endswith("_client"):
            name = attr_name.removesuffix("_client")
            if name not in _EXCLUDED_CLIENTS:
                clients[name] = value
    return clients


def _check_client(name: str, client) -> dict:
    """Check health of a single client."""
    if hasattr(client, "health_check"):
        try:
            result = client.health_check()
            if not result.get("connected", True):
                return {**result, "_degraded": True}
            return result
        except Exception as e:
            return {"connected": False, "status": "error", "error": str(e), "_degraded": True}
    return {"status": "ok"}


@health_router.get("/health")
async def health_check(
    request: Request,
    services: Optional[str] = Query(None, description="Comma-separated list of services to check"),
):
    """Health check endpoint with convention-based client discovery."""
    start_time = time.time()

    health_status = {
        "status": "healthy",
        "service": "backend",
        "timestamp": int(start_time),
    }

    # Parse services filter
    services_filter = None
    if services:
        services_filter = {s.strip().lower() for s in services.split(",")}

    # Discover and check clients
    clients = _discover_clients(request.app)
    for name, client in clients.items():
        if services_filter and name not in services_filter:
            continue
        result = _check_client(name, client)
        if result.pop("_degraded", False):
            health_status["status"] = "degraded"
        health_status[name] = result

    # Add dev info when error exposure is enabled
    if conf.get_http_expose_errors():
        health_status["dev_info"] = {
            "version": get_app_version(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "features": {name: True for name in clients},
            "configuration": {
                "log_level": conf.get_log_level(),
                "http_autoreload": conf.env.parse(conf.HTTP_AUTORELOAD),
            },
        }

    health_status["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
    return health_status
