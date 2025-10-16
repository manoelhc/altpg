"""
Example demonstrating connection pooling with altpg.

Connection pooling allows you to efficiently manage multiple database connections,
improving performance when handling many concurrent requests.
"""

import altpg

# Create a connection pool
pool = altpg.ConnectionPool(
    host='localhost',
    port=5432,
    user='postgres',
    password='password',
    dbname='mydb',
    min_size=2,   # Minimum connections to keep open
    max_size=10   # Maximum connections allowed
)

# Get a connection from the pool
conn1 = pool.get_connection()
cursor1 = conn1.cursor()
cursor1.execute("SELECT * FROM users WHERE id = 1")
print(cursor1.fetchone())
cursor1.close()
conn1.close()

# Get another connection
conn2 = pool.get_connection()
cursor2 = conn2.cursor()
cursor2.execute("SELECT * FROM products LIMIT 10")
for row in cursor2:
    print(row)
cursor2.close()
conn2.close()

# Using context manager
with altpg.ConnectionPool(
    host='localhost',
    dbname='mydb',
    user='postgres',
    password='password',
    min_size=5,
    max_size=20
) as pool:
    # Use multiple connections from the pool
    connections = []
    for i in range(5):
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT {i} as value")
        result = cursor.fetchone()
        print(f"Connection {i}: {result}")
        cursor.close()
        connections.append(conn)
    
    # Close all connections
    for conn in connections:
        conn.close()
    
    # Pool automatically closes on exit
