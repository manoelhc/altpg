"""Tests for SQLAlchemy integration with altpg."""

import pytest

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.pool import NullPool
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False


@pytest.mark.skipif(not SQLALCHEMY_AVAILABLE, reason="SQLAlchemy not installed")
def test_sqlalchemy_dialect_import():
    """Test that SQLAlchemy dialect can be imported."""
    from altpg.sqlalchemy import AltpgDialect
    assert AltpgDialect is not None


@pytest.mark.skipif(not SQLALCHEMY_AVAILABLE, reason="SQLAlchemy not installed")
def test_sqlalchemy_dialect_driver():
    """Test that dialect has correct driver name."""
    from altpg.sqlalchemy import AltpgDialect
    assert AltpgDialect.driver == 'altpg'


@pytest.mark.skipif(not SQLALCHEMY_AVAILABLE, reason="SQLAlchemy not installed")
def test_sqlalchemy_dbapi():
    """Test that dialect returns altpg as DBAPI."""
    from altpg.sqlalchemy import AltpgDialect
    import altpg
    
    dbapi = AltpgDialect.dbapi()
    assert dbapi is altpg


# Note: Actual database connection tests would require a running PostgreSQL instance
# These are commented out but show how to use SQLAlchemy with altpg:
#
# @pytest.mark.skipif(not SQLALCHEMY_AVAILABLE, reason="SQLAlchemy not installed")
# def test_sqlalchemy_engine_creation():
#     """Test creating SQLAlchemy engine with altpg."""
#     engine = create_engine(
#         'postgresql+altpg://postgres:password@localhost/testdb',
#         poolclass=NullPool
#     )
#     assert engine is not None
#
# @pytest.mark.skipif(not SQLALCHEMY_AVAILABLE, reason="SQLAlchemy not installed")
# def test_sqlalchemy_basic_query():
#     """Test basic query with SQLAlchemy using altpg."""
#     engine = create_engine(
#         'postgresql+altpg://postgres:password@localhost/testdb',
#         poolclass=NullPool
#     )
#     
#     with engine.connect() as conn:
#         result = conn.execute(text("SELECT 1 AS value"))
#         row = result.fetchone()
#         assert row[0] == 1
