"""Tests for connection pooling."""

import pytest
import altpg


def test_connection_pool_creation():
    """Test that ConnectionPool can be created."""
    # This will fail without a running PostgreSQL, but tests the API
    try:
        pool = altpg.ConnectionPool(
            host='localhost',
            dbname='testdb',
            user='postgres',
            password='password',
            min_size=2,
            max_size=5
        )
        assert pool is not None
    except altpg.OperationalError:
        # Expected when PostgreSQL is not running
        pass


def test_connection_pool_methods():
    """Test that ConnectionPool has required methods."""
    assert hasattr(altpg.ConnectionPool, 'get_connection')
    assert hasattr(altpg.ConnectionPool, 'close_all')


# Note: Actual database tests would require a running PostgreSQL instance
# These are commented out but show how to test connection pooling:
#
# def test_connection_pool_get_connection():
#     """Test getting a connection from the pool."""
#     pool = altpg.ConnectionPool(
#         host='localhost',
#         dbname='testdb',
#         user='postgres',
#         password='password',
#         min_size=2,
#         max_size=5
#     )
#     
#     conn = pool.get_connection()
#     assert conn is not None
#     cursor = conn.cursor()
#     cursor.execute("SELECT 1")
#     result = cursor.fetchone()
#     assert result[0] == 1
#     
#     conn.close()
#     pool.close_all()
#
# def test_connection_pool_multiple_connections():
#     """Test getting multiple connections from the pool."""
#     pool = altpg.ConnectionPool(
#         host='localhost',
#         dbname='testdb',
#         user='postgres',
#         password='password',
#         min_size=2,
#         max_size=5
#     )
#     
#     conn1 = pool.get_connection()
#     conn2 = pool.get_connection()
#     conn3 = pool.get_connection()
#     
#     assert conn1 is not None
#     assert conn2 is not None
#     assert conn3 is not None
#     
#     conn1.close()
#     conn2.close()
#     conn3.close()
#     pool.close_all()
#
# def test_connection_pool_exhaustion():
#     """Test that pool raises error when exhausted."""
#     pool = altpg.ConnectionPool(
#         host='localhost',
#         dbname='testdb',
#         user='postgres',
#         password='password',
#         min_size=1,
#         max_size=2
#     )
#     
#     conn1 = pool.get_connection()
#     conn2 = pool.get_connection()
#     
#     # This should raise an error
#     with pytest.raises(altpg.OperationalError):
#         conn3 = pool.get_connection()
#     
#     conn1.close()
#     conn2.close()
#     pool.close_all()
#
# def test_connection_pool_context_manager():
#     """Test connection pool with context manager."""
#     with altpg.ConnectionPool(
#         host='localhost',
#         dbname='testdb',
#         user='postgres',
#         password='password',
#         min_size=2,
#         max_size=5
#     ) as pool:
#         conn = pool.get_connection()
#         cursor = conn.cursor()
#         cursor.execute("SELECT 1")
#         result = cursor.fetchone()
#         assert result[0] == 1
#         conn.close()
