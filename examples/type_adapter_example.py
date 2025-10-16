"""
Example demonstrating type adapters and data type handling with altpg.

This shows how altpg handles various PostgreSQL data types.
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

cursor = conn.cursor()

# Integer types
print("Integer Types:")
cursor.execute("SELECT 42::smallint, 12345::integer, 9223372036854775807::bigint")
row = cursor.fetchone()
print(f"  smallint: {row[0]}, integer: {row[1]}, bigint: {row[2]}")

# Floating point types
print("\nFloating Point Types:")
cursor.execute("SELECT 3.14::real, 2.718281828::double precision")
row = cursor.fetchone()
print(f"  real: {row[0]}, double precision: {row[1]}")

# String types
print("\nString Types:")
cursor.execute("SELECT 'Hello'::text, 'World'::varchar(50)")
row = cursor.fetchone()
print(f"  text: {row[0]}, varchar: {row[1]}")

# Boolean type
print("\nBoolean Type:")
cursor.execute("SELECT true, false")
row = cursor.fetchone()
print(f"  true: {row[0]}, false: {row[1]}")

# NULL handling
print("\nNULL Handling:")
cursor.execute("SELECT NULL, 'not null', NULL")
row = cursor.fetchone()
print(f"  NULL: {row[0]}, not null: {row[1]}, NULL: {row[2]}")

# Binary data (bytea)
print("\nBinary Data (bytea):")
cursor.execute("SELECT '\\xDEADBEEF'::bytea")
row = cursor.fetchone()
print(f"  bytea: {row[0]}")

# JSON type
print("\nJSON Type:")
cursor.execute("SELECT '{\"name\": \"Alice\", \"age\": 30}'::json")
row = cursor.fetchone()
print(f"  json: {row[0]}")

# Multiple rows with different types
print("\nMultiple Rows:")
cursor.execute("""
    SELECT 
        id,
        name,
        active,
        score
    FROM (
        VALUES 
            (1, 'Alice', true, 95.5),
            (2, 'Bob', false, 87.3),
            (3, 'Charlie', true, 92.1)
    ) AS t(id, name, active, score)
""")
for row in cursor:
    print(f"  ID: {row[0]}, Name: {row[1]}, Active: {row[2]}, Score: {row[3]}")

cursor.close()
conn.close()

print("\naltpg supports a wide range of PostgreSQL data types!")
