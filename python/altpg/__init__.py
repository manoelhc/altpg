"""
altpg - PostgreSQL Python driver alternative to psycopg

A high-performance PostgreSQL adapter written in Rust using PyO3,
designed to be a drop-in replacement for psycopg2.
"""

from altpg._altpg import (
    connect,
    Connection,
    Cursor,
    DatabaseError,
    IntegrityError,
    ProgrammingError,
    OperationalError,
    InterfaceError,
    apilevel,
    threadsafety,
    paramstyle,
)

__version__ = "0.1.0"
__all__ = [
    "connect",
    "Connection",
    "Cursor",
    "DatabaseError",
    "IntegrityError",
    "ProgrammingError",
    "OperationalError",
    "InterfaceError",
    "apilevel",
    "threadsafety",
    "paramstyle",
]

# DB-API 2.0 module attributes
apilevel = apilevel()
threadsafety = threadsafety()
paramstyle = paramstyle()
