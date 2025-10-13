"""Basic tests for altpg module."""

import pytest
import altpg


def test_module_attributes():
    """Test that module has required DB-API 2.0 attributes."""
    assert altpg.apilevel == "2.0"
    assert altpg.threadsafety == 2
    assert altpg.paramstyle == "pyformat"


def test_exception_hierarchy():
    """Test that exception classes exist and have correct hierarchy."""
    assert hasattr(altpg, 'DatabaseError')
    assert hasattr(altpg, 'IntegrityError')
    assert hasattr(altpg, 'ProgrammingError')
    assert hasattr(altpg, 'OperationalError')
    assert hasattr(altpg, 'InterfaceError')
    
    # Test exception hierarchy
    assert issubclass(altpg.IntegrityError, altpg.DatabaseError)
    assert issubclass(altpg.ProgrammingError, altpg.DatabaseError)
    assert issubclass(altpg.OperationalError, altpg.DatabaseError)


def test_connect_function_exists():
    """Test that connect function exists."""
    assert hasattr(altpg, 'connect')
    assert callable(altpg.connect)


def test_connection_class_exists():
    """Test that Connection class exists."""
    assert hasattr(altpg, 'Connection')


def test_cursor_class_exists():
    """Test that Cursor class exists."""
    assert hasattr(altpg, 'Cursor')


# Note: Actual database connection tests would require a running PostgreSQL instance
# These are commented out but show how to use the library:
#
# def test_connection_basic():
#     """Test basic connection functionality."""
#     conn = altpg.connect(
#         host='localhost',
#         port=5432,
#         user='postgres',
#         password='password',
#         dbname='testdb'
#     )
#     assert conn is not None
#     conn.close()
#
# def test_cursor_basic():
#     """Test basic cursor functionality."""
#     conn = altpg.connect(
#         host='localhost',
#         port=5432,
#         user='postgres',
#         password='password',
#         dbname='testdb'
#     )
#     cursor = conn.cursor()
#     assert cursor is not None
#     cursor.close()
#     conn.close()
