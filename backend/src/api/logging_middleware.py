"""
Request Logging Middleware

Feature 5: Database Management REST API
Logs all API requests for monitoring and debugging
"""

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests"""

    async def dispatch(self, request: Request, call_next):
        """Log request and response details"""
        start_time = time.time()

        # Log request
        logger.info(f"→ {request.method} {request.url.path}")

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time
        duration_ms = int(duration * 1000)

        # Log response
        logger.info(
            f"← {request.method} {request.url.path} "
            f"- {response.status_code} ({duration_ms}ms)"
        )

        return response
