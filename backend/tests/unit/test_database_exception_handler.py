"""Pruebas unitarias para excepciones de base de datos offline o inaccesible."""

from sqlalchemy.exc import InterfaceError, OperationalError

from app.api.v1.schemas.response_schema import create_error_response
from app.core.constants import (
    DATABASE_UNAVAILABLE_DETAIL,
    DATABASE_UNAVAILABLE_MESSAGE,
    ApiErrorCode,
)
from app.domain.exceptions.base import DatabaseConnectionException
from app.main import app, is_database_connection_error


def test_is_database_connection_error_direct():
    """Valida la detección directa de errores de conectividad con la base de datos."""
    # OperationalError de SQLAlchemy
    err_op = OperationalError(
        statement="SELECT 1",
        params={},
        orig=Exception("connection to server at localhost:5432 failed: refused"),
    )
    assert is_database_connection_error(err_op) is True

    # InterfaceError de SQLAlchemy
    err_if = InterfaceError(
        statement="SELECT 1", params={}, orig=Exception("connection reset")
    )
    assert is_database_connection_error(err_if) is True

    # DatabaseConnectionException de dominio
    err_db = DatabaseConnectionException()
    assert is_database_connection_error(err_db) is True

    # ConnectionRefusedError nativa
    err_ref = ConnectionRefusedError("[Errno 111] Connection refused")
    assert is_database_connection_error(err_ref) is True


def test_is_database_connection_error_wrapped():
    """Valida la detección en excepciones anidadas (__cause__ o __context__)."""
    err = RuntimeError("Fallo crítico en capa de persistencia")
    err.__cause__ = ConnectionRefusedError("Connection refused on port 5432")
    assert is_database_connection_error(err) is True

    err_context = RuntimeError("Error en repositorio")
    err_context.__context__ = OperationalError(
        statement="SELECT 1",
        params={},
        orig=Exception("server closed the connection unexpectedly"),
    )
    assert is_database_connection_error(err_context) is True


def test_is_database_connection_error_non_db():
    """Verifica que errores no vinculados a base de datos retornen False."""
    assert is_database_connection_error(ValueError("Parámetro inválido")) is False
    assert is_database_connection_error(KeyError("clave_inexistente")) is False
    assert (
        is_database_connection_error(RuntimeError("Fallo inesperado de CPU"))
        is False
    )


def test_exception_handlers_registered_in_fastapi():
    """Verifica que los handlers específicos estén registrados en FastAPI."""
    registered = app.exception_handlers
    assert OperationalError in registered
    assert DatabaseConnectionException in registered
    assert Exception in registered


def test_database_connection_error_response_payload():
    """Verifica la anatomía del payload ApiResponse devuelto para errores de BD."""
    response = create_error_response(
        message=DATABASE_UNAVAILABLE_MESSAGE,
        status_code=503,
        errors=[{
            "code": ApiErrorCode.DATABASE_CONNECTION_ERROR,
            "detail": DATABASE_UNAVAILABLE_DETAIL,
            "field": "database",
        }],
    )
    payload = response.model_dump(mode="json")
    assert payload["success"] is False
    assert payload["status_code"] == 503
    assert (
        payload["message"]
        == "No se pudo establecer conexión con el servicio de base de datos."
    )
    assert payload["data"] is None
    assert payload["errors"][0]["code"] == "DATABASE_CONNECTION_ERROR"
    assert payload["errors"][0]["field"] == "database"
