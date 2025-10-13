"""
Example usage of altpg - PostgreSQL Python driver

This example demonstrates basic usage of altpg as a drop-in replacement for psycopg2.
"""

import altpg

# Example 1: Basic connection and query
def basic_connection_example():
    """Basic connection example."""
    print("Example 1: Basic Connection")
    print("-" * 40)
    
    # Connect to PostgreSQL database
    # Note: Replace with your actual database credentials
    try:
        conn = altpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='password',
            dbname='testdb'
        )
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Execute a query
        cursor.execute("SELECT version()")
        
        # Fetch results
        result = cursor.fetchone()
        print(f"PostgreSQL version: {result}")
        
        # Close cursor and connection
        cursor.close()
        conn.close()
        
        print("Connection successful!")
    except altpg.OperationalError as e:
        print(f"Could not connect to database: {e}")
    print()


# Example 2: Using connection as context manager
def context_manager_example():
    """Context manager example."""
    print("Example 2: Context Manager")
    print("-" * 40)
    
    try:
        with altpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='password',
            dbname='testdb'
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                print(f"Result: {result}")
        
        print("Query executed successfully!")
    except altpg.OperationalError as e:
        print(f"Could not connect to database: {e}")
    print()


# Example 3: Transaction management
def transaction_example():
    """Transaction management example."""
    print("Example 3: Transaction Management")
    print("-" * 40)
    
    try:
        conn = altpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='password',
            dbname='testdb'
        )
        
        cursor = conn.cursor()
        
        # Execute multiple queries in a transaction
        cursor.execute("CREATE TABLE IF NOT EXISTS test (id INT, name TEXT)")
        cursor.execute("INSERT INTO test VALUES (1, 'Alice')")
        cursor.execute("INSERT INTO test VALUES (2, 'Bob')")
        
        # Commit the transaction
        conn.commit()
        
        # Query the data
        cursor.execute("SELECT * FROM test")
        results = cursor.fetchall()
        print(f"Results: {results}")
        
        cursor.close()
        conn.close()
        
        print("Transaction completed successfully!")
    except altpg.ProgrammingError as e:
        print(f"Query error: {e}")
    except altpg.OperationalError as e:
        print(f"Could not connect to database: {e}")
    print()


# Example 4: Error handling
def error_handling_example():
    """Error handling example."""
    print("Example 4: Error Handling")
    print("-" * 40)
    
    try:
        conn = altpg.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='password',
            dbname='testdb'
        )
        
        cursor = conn.cursor()
        
        try:
            # This will fail if the table doesn't exist
            cursor.execute("SELECT * FROM nonexistent_table")
        except altpg.ProgrammingError as e:
            print(f"Query failed as expected: {e}")
            conn.rollback()  # Roll back the failed transaction
        
        cursor.close()
        conn.close()
        
    except altpg.OperationalError as e:
        print(f"Could not connect to database: {e}")
    print()


# Display DB-API 2.0 information
def display_db_api_info():
    """Display DB-API 2.0 information."""
    print("DB-API 2.0 Information")
    print("-" * 40)
    print(f"API Level: {altpg.apilevel}")
    print(f"Thread Safety: {altpg.threadsafety}")
    print(f"Parameter Style: {altpg.paramstyle}")
    print()


if __name__ == "__main__":
    print("=" * 50)
    print("altpg - PostgreSQL Python Driver Examples")
    print("=" * 50)
    print()
    
    display_db_api_info()
    
    print("Note: The following examples require a running PostgreSQL instance.")
    print("Update the connection parameters in the examples to match your setup.")
    print()
    
    # Uncomment the examples you want to run:
    # basic_connection_example()
    # context_manager_example()
    # transaction_example()
    # error_handling_example()
