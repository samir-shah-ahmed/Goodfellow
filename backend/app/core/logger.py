import json
import logging
import sys
import time
import uuid
from contextvars import ContextVar
from typing import Any, Dict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# Context to carry request ID across the request lifetime
_request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")

class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # Attach request_id to every record
        record.request_id = _request_id_ctx.get()
        return True

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "ts": int(time.time() * 1000),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)

def setup_logging(level: str = "INFO", fmt: str = "plain") -> None:
    """
    level: "DEBUG" | "INFO" | "WARNING" | "ERROR"
    fmt:   "plain" | "json"
    """
    root = logging.getLogger()
    root.handlers = []  # reset any prior basicConfig
    root.setLevel(level.upper())

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestIdFilter())

    if fmt.lower() == "json":
        handler.setFormatter(JsonFormatter())
    else:
        # Include request_id token in plain logs too
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | req_id=%(request_id)s | %(message)s"
        ))

    root.addHandler(handler)

def get_logger(name: str = "balanced-alpha") -> logging.Logger:
    return logging.getLogger(name)

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        token = _request_id_ctx.set(req_id)  # set context for this request
        request.state.request_id = req_id
        try:
            response = await call_next(request)
        finally:
            _request_id_ctx.reset(token)  # clean up context
        response.headers["X-Request-ID"] = req_id
        return response