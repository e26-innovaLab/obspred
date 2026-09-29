"""Módulo de excepciones del dominio."""

from app.domain.exceptions.base import DomainException, EntityNotFoundException

__all__ = ["DomainException", "EntityNotFoundException"]
