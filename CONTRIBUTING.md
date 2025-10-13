# Contributing to altpg

Thank you for your interest in contributing to altpg! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Rust 1.65 or later
- Python 3.8 or later
- PostgreSQL 9.6 or later (for integration tests)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/manoelhc/altpg.git
cd altpg
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install maturin pytest pytest-asyncio sqlalchemy
```

4. Build and install in development mode:
```bash
maturin develop
```

## Building

To build the project:

```bash
# Development build
maturin build

# Release build (optimized)
maturin build --release
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_basic.py -v

# Run with coverage
pytest tests/ --cov=altpg --cov-report=html
```

### Integration Tests

Integration tests require a running PostgreSQL instance. Set up a test database:

```bash
createdb altpg_test
export DATABASE_URL="postgresql://postgres:password@localhost/altpg_test"
pytest tests/integration/ -v
```

## Code Style

### Rust

We follow standard Rust formatting:

```bash
# Format code
cargo fmt

# Check formatting
cargo fmt -- --check

# Run linter
cargo clippy

# Run linter with all warnings as errors
cargo clippy -- -D warnings
```

### Python

We follow PEP 8 style guidelines:

```bash
# Format code with black
black python/

# Check with flake8
flake8 python/

# Type checking with mypy
mypy python/
```

## Pull Request Process

1. Fork the repository
2. Create a new branch for your feature (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and ensure they pass
5. Run formatters and linters
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### PR Guidelines

- Write clear, descriptive commit messages
- Include tests for new features
- Update documentation as needed
- Ensure all tests pass
- Keep PRs focused on a single feature or fix

## Feature Requests and Bug Reports

Please use GitHub Issues to report bugs or request features:

- **Bug Reports**: Include steps to reproduce, expected behavior, and actual behavior
- **Feature Requests**: Describe the feature and its use case

## Development Priorities

Current priorities for development:

1. **Core Functionality**
   - Complete type adapter system
   - Parameter binding improvements
   - Result fetching optimization

2. **Advanced Features**
   - Server-side cursors
   - COPY operations
   - NOTIFY/LISTEN support
   - Connection pooling

3. **Compatibility**
   - Full psycopg2/psycopg3 compatibility
   - SQLAlchemy dialect improvements
   - Django backend support

4. **Performance**
   - Benchmarking suite
   - Performance optimization
   - Memory usage optimization

5. **Testing**
   - Comprehensive test suite
   - Integration tests with real PostgreSQL
   - Compatibility tests with ORMs

## Architecture

### Project Structure

```
altpg/
├── src/
│   └── lib.rs              # Rust implementation
├── python/
│   └── altpg/
│       ├── __init__.py     # Python wrapper
│       └── sqlalchemy/     # SQLAlchemy dialect
├── tests/                  # Test suite
├── examples/               # Usage examples
├── Cargo.toml             # Rust dependencies
└── pyproject.toml         # Python package config
```

### Key Components

1. **Rust Core** (`src/lib.rs`):
   - Connection management
   - Query execution
   - Type conversion
   - Error handling

2. **Python Wrapper** (`python/altpg/__init__.py`):
   - DB-API 2.0 interface
   - Exception classes
   - Module-level attributes

3. **SQLAlchemy Dialect** (`python/altpg/sqlalchemy/`):
   - SQLAlchemy integration
   - Dialect registration

## Resources

- [PyO3 Documentation](https://pyo3.rs/)
- [rust-postgres Documentation](https://docs.rs/postgres/)
- [Python DB-API 2.0 Specification](https://www.python.org/dev/peps/pep-0249/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

## License

By contributing to altpg, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to open an issue for any questions or join discussions in the repository.
