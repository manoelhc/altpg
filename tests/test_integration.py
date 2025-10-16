"""
Comprehensive integration tests for altpg with real PostgreSQL.

These tests require a running PostgreSQL instance.
They can be skipped with: pytest -m "not integration"
"""

import pytest
import altpg


# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture
def db_connection():
    """Fixture to provide a database connection for tests."""
    conn = None
    try:
        conn = altpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='password',
            dbname='testdb'
        )
        yield conn
    except altpg.OperationalError:
        pytest.skip("PostgreSQL not available")
    finally:
        if conn:
            conn.close()


@pytest.fixture
def clean_table(db_connection):
    """Fixture to create and cleanup a test table."""
    cursor = db_connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS test_table")
    cursor.execute("""
        CREATE TABLE test_table (
            id SERIAL PRIMARY KEY,
            name TEXT,
            age INTEGER,
            email TEXT,
            active BOOLEAN,
            score REAL
        )
    """)
    db_connection.commit()
    
    yield
    
    cursor.execute("DROP TABLE IF EXISTS test_table")
    db_connection.commit()
    cursor.close()


class TestBasicQueries:
    """Test basic query operations."""
    
    def test_select_literal(self, db_connection):
        """Test simple SELECT with literal value."""
        cursor = db_connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1
        cursor.close()
    
    def test_select_multiple_columns(self, db_connection):
        """Test SELECT with multiple columns."""
        cursor = db_connection.cursor()
        cursor.execute("SELECT 1, 'hello', TRUE, 3.14")
        result = cursor.fetchone()
        assert len(result) == 4
        assert result[0] == 1
        assert result[1] == 'hello'
        assert result[2] is True
        assert abs(result[3] - 3.14) < 0.01
        cursor.close()
    
    def test_select_multiple_rows(self, db_connection):
        """Test SELECT returning multiple rows."""
        cursor = db_connection.cursor()
        cursor.execute("SELECT generate_series(1, 5)")
        results = cursor.fetchall()
        assert len(results) == 5
        for i, row in enumerate(results, 1):
            assert row[0] == i
        cursor.close()


class TestCRUDOperations:
    """Test Create, Read, Update, Delete operations."""
    
    def test_insert_single_row(self, db_connection, clean_table):
        """Test inserting a single row."""
        cursor = db_connection.cursor()
        cursor.execute("""
            INSERT INTO test_table (name, age, email, active, score)
            VALUES ('John Doe', 30, 'john@example.com', TRUE, 95.5)
        """)
        assert cursor.rowcount == 1
        db_connection.commit()
        
        cursor.execute("SELECT * FROM test_table WHERE name = 'John Doe'")
        result = cursor.fetchone()
        assert result is not None
        cursor.close()
    
    def test_insert_multiple_rows(self, db_connection, clean_table):
        """Test inserting multiple rows."""
        cursor = db_connection.cursor()
        for i in range(5):
            cursor.execute("""
                INSERT INTO test_table (name, age)
                VALUES (%s, %s)
            """, (f'User {i}', 20 + i))
        db_connection.commit()
        
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count = cursor.fetchone()[0]
        assert count == 5
        cursor.close()
    
    def test_update_rows(self, db_connection, clean_table):
        """Test updating rows."""
        cursor = db_connection.cursor()
        cursor.execute("INSERT INTO test_table (name, age) VALUES ('Alice', 25)")
        db_connection.commit()
        
        cursor.execute("UPDATE test_table SET age = 26 WHERE name = 'Alice'")
        assert cursor.rowcount == 1
        db_connection.commit()
        
        cursor.execute("SELECT age FROM test_table WHERE name = 'Alice'")
        result = cursor.fetchone()
        assert result[0] == 26
        cursor.close()
    
    def test_delete_rows(self, db_connection, clean_table):
        """Test deleting rows."""
        cursor = db_connection.cursor()
        cursor.execute("INSERT INTO test_table (name, age) VALUES ('Bob', 30)")
        db_connection.commit()
        
        cursor.execute("DELETE FROM test_table WHERE name = 'Bob'")
        assert cursor.rowcount == 1
        db_connection.commit()
        
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count = cursor.fetchone()[0]
        assert count == 0
        cursor.close()


class TestTransactions:
    """Test transaction handling."""
    
    def test_commit(self, db_connection, clean_table):
        """Test transaction commit."""
        cursor = db_connection.cursor()
        cursor.execute("INSERT INTO test_table (name) VALUES ('Test')")
        db_connection.commit()
        
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count = cursor.fetchone()[0]
        assert count == 1
        cursor.close()
    
    def test_rollback(self, db_connection, clean_table):
        """Test transaction rollback."""
        cursor = db_connection.cursor()
        cursor.execute("INSERT INTO test_table (name) VALUES ('Test')")
        db_connection.rollback()
        
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count = cursor.fetchone()[0]
        assert count == 0
        cursor.close()


class TestCursorFeatures:
    """Test cursor-specific features."""
    
    def test_description(self, db_connection, clean_table):
        """Test cursor description attribute."""
        cursor = db_connection.cursor()
        cursor.execute("SELECT id, name, age FROM test_table")
        
        desc = cursor.description
        assert desc is not None
        assert len(desc) == 3
        assert desc[0][0] == 'id'
        assert desc[1][0] == 'name'
        assert desc[2][0] == 'age'
        cursor.close()
    
    def test_rowcount(self, db_connection, clean_table):
        """Test cursor rowcount attribute."""
        cursor = db_connection.cursor()
        cursor.execute("INSERT INTO test_table (name) VALUES ('Test')")
        assert cursor.rowcount == 1
        
        cursor.execute("SELECT * FROM test_table")
        assert cursor.rowcount >= 0
        cursor.close()
    
    def test_fetchmany(self, db_connection):
        """Test fetchmany method."""
        cursor = db_connection.cursor()
        cursor.execute("SELECT generate_series(1, 100)")
        
        batch1 = cursor.fetchmany(10)
        assert len(batch1) == 10
        
        batch2 = cursor.fetchmany(20)
        assert len(batch2) == 20
        
        cursor.close()
    
    def test_iteration(self, db_connection):
        """Test cursor iteration."""
        cursor = db_connection.cursor()
        cursor.execute("SELECT generate_series(1, 10)")
        
        count = 0
        for row in cursor:
            count += 1
        
        assert count == 10
        cursor.close()


class TestContextManagers:
    """Test context manager support."""
    
    def test_connection_context_manager(self, clean_table):
        """Test connection as context manager."""
        with altpg.connect(host='localhost', dbname='testdb', 
                          user='postgres', password='password') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
            cursor.close()
    
    def test_cursor_context_manager(self, db_connection):
        """Test cursor as context manager."""
        with db_connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1


class TestErrorHandling:
    """Test error handling and exceptions."""
    
    def test_syntax_error(self, db_connection):
        """Test handling of SQL syntax errors."""
        cursor = db_connection.cursor()
        with pytest.raises(altpg.ProgrammingError):
            cursor.execute("SELCT 1")  # Typo
        cursor.close()
    
    def test_connection_after_close(self):
        """Test operations on closed connection."""
        try:
            conn = altpg.connect(host='localhost', dbname='testdb',
                                user='postgres', password='password')
            conn.close()
            
            with pytest.raises(altpg.InterfaceError):
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
        except altpg.OperationalError:
            pytest.skip("PostgreSQL not available")
    
    def test_invalid_connection(self):
        """Test connection to invalid database."""
        with pytest.raises(altpg.OperationalError):
            altpg.connect(host='localhost', dbname='nonexistent_db',
                         user='postgres', password='wrong_password')


class TestDataTypes:
    """Test various PostgreSQL data types."""
    
    def test_text_types(self, db_connection):
        """Test text and varchar types."""
        cursor = db_connection.cursor()
        cursor.execute("SELECT 'hello'::text, 'world'::varchar")
        result = cursor.fetchone()
        assert result[0] == 'hello'
        assert result[1] == 'world'
        cursor.close()
    
    def test_numeric_types(self, db_connection):
        """Test various numeric types."""
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT 
                42::smallint,
                12345::integer,
                9223372036854775807::bigint,
                3.14::real,
                2.718281828::double precision
        """)
        result = cursor.fetchone()
        assert result[0] == 42
        assert result[1] == 12345
        assert result[2] == 9223372036854775807
        assert abs(result[3] - 3.14) < 0.01
        assert abs(result[4] - 2.718281828) < 0.000001
        cursor.close()
    
    def test_boolean_type(self, db_connection):
        """Test boolean type."""
        cursor = db_connection.cursor()
        cursor.execute("SELECT TRUE, FALSE")
        result = cursor.fetchone()
        assert result[0] is True
        assert result[1] is False
        cursor.close()
    
    def test_null_values(self, db_connection):
        """Test NULL handling."""
        cursor = db_connection.cursor()
        cursor.execute("SELECT NULL, 1, NULL")
        result = cursor.fetchone()
        assert result[0] is None
        assert result[1] == 1
        assert result[2] is None
        cursor.close()


# Configuration for pytest
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test requiring PostgreSQL"
    )
