"""Прокси-модуль для совместимости — re-экспортирует из app.database."""

from app.database import (
    get_db as get_session,        # alias: новые роутеры используют get_session
    get_engine as _get_engine,
    _session_factory,             # noqa: F401 — используется в security.py
)


def _async_engine_property():
    """Ленивое получение движка для SQLAdmin."""
    try:
        return _get_engine()
    except RuntimeError:
        return None


# SQLAdmin требует объект engine, а не корутину.
# Используем прокси-дескриптор.
class _EngineProxy:
    """Ленивый прокси к AsyncEngine, чтобы admin.py импортировался до init БД."""

    def __getattr__(self, name):
        return getattr(_get_engine(), name)

    def __repr__(self):
        try:
            return repr(_get_engine())
        except RuntimeError:
            return "<EngineProxy (not initialized)>"


async_engine = _EngineProxy()

__all__ = ["get_session", "async_engine", "_session_factory"]
