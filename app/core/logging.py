import logging
import sys
import time
import uuid
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("eastvantage.address_book")


def configure_logging(log_level: str = "INFO") -> None:
    log_format = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
    date_format = "%Y-%m-%dT%H:%M:%S%z"

    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Measure request latency and attach a UUID correlation ID to response headers."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start_time = time.perf_counter()

        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path

        logger.info(
            f"HTTP request started: id={request_id} client={client_ip} method={method} path={path}"
        )

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000
            response.headers["X-Request-ID"] = request_id

            logger.info(
                f"HTTP request completed: id={request_id} method={method} path={path} "
                f"status={response.status_code} duration={duration_ms:.2f}ms"
            )
            return response
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.exception(
                f"HTTP request failed: id={request_id} method={method} path={path} "
                f"duration={duration_ms:.2f}ms error={exc}"
            )
            raise
