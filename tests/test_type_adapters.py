"""Tests for type adapter system."""

import pytest
import altpg


def test_type_adapters_exist():
    """Test that type adapter infrastructure exists."""
    # Basic types should be supported through the type conversion system
    assert hasattr(altpg, 'connect')
    
    # The actual type conversion happens in Rust
    # This test ensures the structure is in place


def test_connection_pool_exists():
    """Test that ConnectionPool class exists."""
    assert hasattr(altpg, 'ConnectionPool')
    assert callable(altpg.ConnectionPool)


# Note: Actual database tests would require a running PostgreSQL instance
# These are commented out but show how to test type adapters:
#
# def test_string_type():
#     """Test string type handling."""
#     conn = altpg.connect(host='localhost', dbname='testdb')
#     cursor = conn.cursor()
#     cursor.execute("SELECT 'hello'::text")
#     result = cursor.fetchone()
#     assert result[0] == 'hello'
#     conn.close()
#
# def test_integer_types():
#     """Test integer type handling."""
#     conn = altpg.connect(host='localhost', dbname='testdb')
#     cursor = conn.cursor()
#     cursor.execute("SELECT 42::integer, 9223372036854775807::bigint")
#     result = cursor.fetchone()
#     assert result[0] == 42
#     assert result[1] == 9223372036854775807
#     conn.close()
#
# def test_float_types():
#     """Test float type handling."""
#     conn = altpg.connect(host='localhost', dbname='testdb')
#     cursor = conn.cursor()
#     cursor.execute("SELECT 3.14::real, 2.718281828::double precision")
#     result = cursor.fetchone()
#     assert abs(result[0] - 3.14) < 0.01
#     assert abs(result[1] - 2.718281828) < 0.000001
#     conn.close()
#
# def test_boolean_type():
#     """Test boolean type handling."""
#     conn = altpg.connect(host='localhost', dbname='testdb')
#     cursor = conn.cursor()
#     cursor.execute("SELECT true::boolean, false::boolean")
#     result = cursor.fetchone()
#     assert result[0] is True
#     assert result[1] is False
#     conn.close()
#
# def test_null_type():
#     """Test NULL handling."""
#     conn = altpg.connect(host='localhost', dbname='testdb')
#     cursor = conn.cursor()
#     cursor.execute("SELECT NULL")
#     result = cursor.fetchone()
#     assert result[0] is None
#     conn.close()
#
# def test_bytea_type():
#     """Test bytea (binary) type handling."""
#     conn = altpg.connect(host='localhost', dbname='testdb')
#     cursor = conn.cursor()
#     cursor.execute("SELECT '\\xDEADBEEF'::bytea")
#     result = cursor.fetchone()
#     assert isinstance(result[0], bytes)
#     conn.close()
#
# def test_json_type():
#     """Test JSON type handling."""
#     conn = altpg.connect(host='localhost', dbname='testdb')
#     cursor = conn.cursor()
#     cursor.execute("SELECT '{\"key\": \"value\"}'::json")
#     result = cursor.fetchone()
#     assert '"key"' in result[0]
#     conn.close()
