# Installation and Setup Guide

## Prerequisites

### For Users (Installing pre-built wheels)

- Python 3.8 or later
- pip

### For Developers (Building from source)

- Python 3.8 or later
- Rust 1.65 or later
- pip
- maturin

## Installation

### Option 1: Install from PyPI (when available)

```bash
pip install altpg
```

### Option 2: Install from Wheel

If you have a pre-built wheel file:

```bash
pip install altpg-*.whl
```

### Option 3: Build and Install from Source

#### Step 1: Install Rust

If you don't have Rust installed, install it using rustup:

**Linux/macOS:**
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

**Windows:**
Download and run [rustup-init.exe](https://rustup.rs/)

#### Step 2: Install maturin

```bash
pip install maturin
```

#### Step 3: Clone the Repository

```bash
git clone https://github.com/manoelhc/altpg.git
cd altpg
```

#### Step 4: Build and Install

**For production use:**
```bash
maturin build --release
pip install target/wheels/altpg-*.whl
```

**For development:**
```bash
# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
maturin develop
```

## Verifying Installation

After installation, verify that altpg is working:

```bash
python -c "import altpg; print(altpg.__version__)"
```

You should see the version number printed.

## Basic Usage Test

Create a test script `test_altpg.py`:

```python
import altpg

# Test module attributes
print(f"API Level: {altpg.apilevel}")
print(f"Thread Safety: {altpg.threadsafety}")
print(f"Parameter Style: {altpg.paramstyle}")

# Test exception classes
print(f"DatabaseError: {altpg.DatabaseError}")
print(f"IntegrityError: {altpg.IntegrityError}")

print("\naltpg is installed correctly!")
```

Run the test:
```bash
python test_altpg.py
```

## Database Connection Setup

### PostgreSQL Installation

If you don't have PostgreSQL installed:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Windows:**
Download and install from [postgresql.org](https://www.postgresql.org/download/windows/)

### Create a Test Database

```bash
# Switch to postgres user (Linux/macOS)
sudo -u postgres psql

# Create a database and user
CREATE DATABASE testdb;
CREATE USER testuser WITH PASSWORD 'testpass';
GRANT ALL PRIVILEGES ON DATABASE testdb TO testuser;
\q
```

### Test Connection

Create a test script `test_connection.py`:

```python
import altpg

try:
    conn = altpg.connect(
        host='localhost',
        port=5432,
        user='testuser',
        password='testpass',
        dbname='testdb'
    )
    print("Connection successful!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT version()")
    version = cursor.fetchone()
    print(f"PostgreSQL version: {version}")
    
    cursor.close()
    conn.close()
except altpg.OperationalError as e:
    print(f"Connection failed: {e}")
```

Run the test:
```bash
python test_connection.py
```

## SQLAlchemy Setup

To use altpg with SQLAlchemy:

```bash
pip install sqlalchemy
```

Test SQLAlchemy integration:

```python
from sqlalchemy import create_engine, text

# Create engine with altpg
engine = create_engine('postgresql+altpg://testuser:testpass@localhost/testdb')

# Test connection
with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print(f"Result: {result.fetchone()}")

print("SQLAlchemy integration working!")
```

## Troubleshooting

### Import Error: No module named 'altpg'

Make sure altpg is installed in the correct Python environment:
```bash
pip list | grep altpg
```

If not found, reinstall:
```bash
pip install altpg
```

### Build Errors with maturin

Make sure you have the latest Rust toolchain:
```bash
rustup update
```

Make sure you have the correct Python development headers:

**Ubuntu/Debian:**
```bash
sudo apt install python3-dev
```

**macOS:**
```bash
brew install python@3.12
```

### Connection Errors

1. Verify PostgreSQL is running:
```bash
sudo systemctl status postgresql  # Linux
brew services list                # macOS
```

2. Check connection parameters:
   - Correct host (usually 'localhost')
   - Correct port (usually 5432)
   - Valid username and password
   - Database exists

3. Check PostgreSQL logs for errors:
```bash
sudo tail -f /var/log/postgresql/postgresql-*.log  # Linux
tail -f /usr/local/var/log/postgres.log            # macOS
```

### Permission Errors

If you get permission errors, make sure your PostgreSQL user has the correct privileges:

```sql
GRANT ALL PRIVILEGES ON DATABASE testdb TO testuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO testuser;
```

## Next Steps

- Read the [README.md](README.md) for usage examples
- Check [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
- Review [examples/](examples/) for code samples
- Run tests with `pytest tests/` to ensure everything works

## Getting Help

- GitHub Issues: [https://github.com/manoelhc/altpg/issues](https://github.com/manoelhc/altpg/issues)
- Documentation: [README.md](README.md)
- Examples: [examples/](examples/)

## Platform-Specific Notes

### Linux
- Usually requires `python3-dev` package
- May need to install `libpq-dev` for PostgreSQL client libraries

### macOS
- Xcode Command Line Tools required
- May need to set `LIBRARY_PATH` for PostgreSQL

### Windows
- Visual Studio Build Tools required
- May need to set environment variables for PostgreSQL

## Performance Tips

1. Use connection pooling for web applications
2. Enable prepared statements for repeated queries
3. Use batched operations for bulk inserts
4. Consider using `COPY` for large data imports (when implemented)

## Security

- Never commit database credentials to version control
- Use environment variables for sensitive configuration
- Always use parameterized queries to prevent SQL injection
- Keep PostgreSQL and altpg updated to the latest versions
