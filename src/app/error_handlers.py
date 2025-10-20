"""Global error handlers for the Fire & Forget Accounting API."""

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.app.exceptions import FireForgetException, create_http_exception

logger = structlog.get_logger()


def setup_error_handlers(app: FastAPI) -> None:
    """Set up global error handlers for the FastAPI application."""

    @app.exception_handler(FireForgetException)
    async def fireforget_exception_handler(request: Request, exc: FireForgetException):
        """Handle custom FireForgetException."""
        logger.error(
            "FireForgetException occurred",
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
            path=request.url.path,
            method=request.method
        )

        http_exc = create_http_exception(exc)
        return JSONResponse(
            status_code=http_exc.status_code,
            content=http_exc.detail
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors."""
        logger.error(
            "Validation error occurred",
            errors=exc.errors(),
            path=request.url.path,
            method=request.method
        )

        return JSONResponse(
            status_code=422,
            content={
                "message": "Request validation failed",
                "error_code": "VALIDATION_ERROR",
                "details": {
                    "errors": exc.errors(),
                    "body": exc.body
                }
            }
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions."""
        logger.error(
            "HTTP exception occurred",
            status_code=exc.status_code,
            detail=exc.detail,
            path=request.url.path,
            method=request.method
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": exc.detail,
                "error_code": f"HTTP_{exc.status_code}",
                "details": {
                    "status_code": exc.status_code
                }
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        logger.error(
            "Unhandled exception occurred",
            exception_type=type(exc).__name__,
            message=str(exc),
            path=request.url.path,
            method=request.method,
            exc_info=True
        )

        return JSONResponse(
            status_code=500,
            content={
                "message": "Internal server error",
                "error_code": "INTERNAL_SERVER_ERROR",
                "details": {
                    "exception_type": type(exc).__name__
                }
            }
        )
