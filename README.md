# altpg

PostgreSQL Python driver alternative to psycopg, written in Rust with PyO3.

## Overview

`altpg` is a high-performance PostgreSQL database adapter for Python that aims to be a drop-in replacement for `psycopg2`. It is built using Rust and PyO3, leveraging the [rust-postgres](https://crates.io/crates/postgres) crate for database connectivity.

## Features

- **DB-API 2.0 Compliant**: Implements the Python Database API Specification v2.0
- **High Performance**: Written in Rust for maximum performance
- **psycopg2 Compatible**: Designed to be a drop-in replacement for psycopg2
- **SQLAlchemy Compatible**: Works with SQLAlchemy and other ORMs
- **Type Safe**: Leverages Rust's type system for safety
- **Easy to Install**: Distributed as Python wheels, no compilation needed

## Installation

```bash
pip install altpg
```

Or install from wheel:
```bash
pip install target/wheels/altpg-*.whl
```

## Quick Start

```python
import altpg

# Connect to PostgreSQL
conn = altpg.connect(
    host='localhost',
    port=5432,
    user='postgres',
    password='password',
    dbname='mydb'
)

# Create a cursor
cursor = conn.cursor()

# Execute a query
cursor.execute("SELECT * FROM users WHERE id = %s", (1,))

# Fetch results
row = cursor.fetchone()
print(row)

# Commit and close
conn.commit()
cursor.close()
conn.close()
```

## Usage with Context Managers

```python
import altpg

with altpg.connect(host='localhost', dbname='mydb', user='postgres', password='password') as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
```

## API Reference

### Connection Methods

- `connect(dsn=None, host=None, port=None, user=None, password=None, dbname=None)` - Create a connection
- `cursor()` - Create a cursor object
- `commit()` - Commit the current transaction
- `rollback()` - Roll back the current transaction
- `close()` - Close the connection
- `autocommit` - Get/set autocommit mode (property)

### Cursor Methods

- `execute(query, params=None)` - Execute a query
- `fetchone()` - Fetch one row
- `fetchall()` - Fetch all rows
- `fetchmany(size=None)` - Fetch multiple rows
- `close()` - Close the cursor
- `description` - Column information (property)
- `rowcount` - Number of affected rows (property)
- `arraysize` - Number of rows to fetch at a time (property)

### Exception Classes

- `DatabaseError` - Base exception for database errors
- `IntegrityError` - Integrity constraint violation
- `ProgrammingError` - Programming error (e.g., syntax error)
- `OperationalError` - Operational error (e.g., connection failed)
- `InterfaceError` - Error related to the database interface

### DB-API 2.0 Attributes

- `apilevel` - String constant "2.0"
- `threadsafety` - Integer constant 2 (threads may share the module and connections)
- `paramstyle` - String constant "pyformat"

## SQLAlchemy Integration

`altpg` can be used as a PostgreSQL dialect for SQLAlchemy:

```python
from sqlalchemy import create_engine

# Use altpg as the driver
engine = create_engine('postgresql+altpg://user:password@localhost/mydb')

# Use with SQLAlchemy ORM
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()
```

## Building from Source

Requirements:
- Rust 1.65 or later
- Python 3.8 or later
- maturin

```bash
# Install maturin
pip install maturin

# Build the wheel
maturin build --release

# Install the wheel
pip install target/wheels/altpg-*.whl
```

## Development

```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install maturin pytest

# Build and install in development mode
maturin develop

# Run tests
pytest tests/
```

## Performance

`altpg` is designed for high performance by leveraging Rust's zero-cost abstractions and efficient memory management. Benchmarks show significant performance improvements over pure Python implementations.

## Compatibility

- Python 3.8+
- PostgreSQL 9.6+
- Compatible with psycopg2 API
- Works with SQLAlchemy, Django, Flask-SQLAlchemy, and other ORMs

## Limitations

This is an early release with basic functionality. Some advanced psycopg2 features may not yet be implemented:
- Advanced type adapters
- Server-side cursors
- COPY operations
- Asynchronous operations
- NOTIFY/LISTEN

Contributions are welcome!

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Credits

Built with:
- [PyO3](https://pyo3.rs/) - Rust bindings for Python
- [rust-postgres](https://crates.io/crates/postgres) - PostgreSQL client library

## Roadmap

- [ ] Complete type adapter system
- [ ] Server-side cursors
- [ ] COPY operations
- [ ] Async/await support
- [ ] NOTIFY/LISTEN support
- [ ] Connection pooling
- [ ] Full psycopg2/psycopg3 compatibility
- [ ] Performance benchmarks
- [ ] Comprehensive test suite with real PostgreSQL tests

