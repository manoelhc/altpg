"""SQLAlchemy dialect for altpg."""

from sqlalchemy.dialects.postgresql.psycopg2 import PGDialect_psycopg2
from sqlalchemy.dialects import registry

import altpg


class AltpgDialect(PGDialect_psycopg2):
    """SQLAlchemy dialect for altpg PostgreSQL driver.
    
    This dialect extends the psycopg2 dialect to provide compatibility
    with altpg while maintaining all PostgreSQL features.
    """
    
    driver = 'altpg'
    supports_native_decimal = True
    
    @classmethod
    def dbapi(cls):
        """Return the altpg module."""
        return altpg
    
    @classmethod
    def import_dbapi(cls):
        """Import and return the altpg module."""
        return altpg


# Register the dialect with SQLAlchemy
registry.register("postgresql.altpg", __name__, "AltpgDialect")

# Also register as a default for ease of use
__all__ = ['AltpgDialect']
