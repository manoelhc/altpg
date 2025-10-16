"""
Example demonstrating server-side cursors with altpg.

Server-side cursors are useful for handling large result sets efficiently,
as they fetch rows in batches rather than loading everything into memory.
"""

import altpg

# Connect to the database
conn = altpg.connect(
    host='localhost',
    port=5432,
    user='postgres',
    password='password',
    dbname='mydb'
)

# Create a regular (client-side) cursor
print("Regular cursor - fetches all results into memory:")
cursor = conn.cursor()
cursor.execute("SELECT * FROM large_table LIMIT 100")
rows = cursor.fetchall()
print(f"Fetched {len(rows)} rows")
cursor.close()

# Create a named (server-side) cursor
print("\nServer-side cursor - fetches results in batches:")
server_cursor = conn.cursor(name='my_server_cursor')
server_cursor.execute("SELECT * FROM large_table")

# Fetch rows in batches
batch_size = 10
while True:
    rows = server_cursor.fetchmany(batch_size)
    if not rows:
        break
    print(f"Processing batch of {len(rows)} rows")
    # Process the rows...

server_cursor.close()

# Using iteration with server-side cursor
print("\nIterating over server-side cursor:")
iter_cursor = conn.cursor(name='iter_cursor')
iter_cursor.execute("SELECT generate_series(1, 100) as num")

for i, row in enumerate(iter_cursor):
    if i >= 5:  # Just show first 5
        break
    print(f"Row {i}: {row}")

iter_cursor.close()
conn.close()

print("\nServer-side cursors help manage memory when dealing with large result sets!")
