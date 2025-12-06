"""Middleware de gestion d'erreurs global pour FastAPI."""
import logging
import uuid
from datetime import datetime
from typing import Dict, Any

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Configuration du logger
logger = logging.getLogger(__name__)


def create_error_response(
    error_type: str,
    message: str,
    status_code: int,
    details: Dict[str, Any] = None,
    trace_id: str = None
) -> JSONResponse:
    """Crée une réponse d'erreur standardisée."""
    response_data = {
        "error": error_type,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    if trace_id:
        response_data["trace_id"] = trace_id
    
    if details:
        response_data["details"] = details
    
    return JSONResponse(
        status_code=status_code,
        content=response_data
    )


async def error_handler_middleware(request: Request, call_next):
    """Middleware de gestion d'erreurs global."""
    trace_id = str(uuid.uuid4())[:8]
    
    try:
        response = await call_next(request)
        return response
        
    except RequestValidationError as e:
        # Erreurs de validation Pydantic (422)
        logger.error(f"Validation error [{trace_id}]: {e.errors()}")
        return create_error_response(
            error_type="validation_error",
            message="Données invalides",
            status_code=422,
            details={"validation_errors": e.errors()},
            trace_id=trace_id
        )
        
    except HTTPException as e:
        # Erreurs HTTP FastAPI (401, 403, 404, etc.)
        logger.warning(f"HTTP error [{trace_id}]: {e.status_code} - {e.detail}")
        return create_error_response(
            error_type="http_error",
            message=str(e.detail),
            status_code=e.status_code,
            trace_id=trace_id
        )
        
    except StarletteHTTPException as e:
        # Erreurs HTTP Starlette
        logger.warning(f"Starlette HTTP error [{trace_id}]: {e.status_code} - {e.detail}")
        return create_error_response(
            error_type="http_error",
            message=str(e.detail),
            status_code=e.status_code,
            trace_id=trace_id
        )
        
    except Exception as e:
        # Erreurs internes (500)
        logger.error(f"Internal error [{trace_id}]: {str(e)}", exc_info=True)
        return create_error_response(
            error_type="internal_error",
            message="Erreur interne du serveur",
            status_code=500,
            trace_id=trace_id
        )


def setup_error_middleware(app):
    """Configure le middleware d'erreurs sur l'app FastAPI."""
    app.middleware("http")(error_handler_middleware)
    logger.info("✅ Middleware d'erreurs global activé")
