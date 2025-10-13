# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-12

### Added
- Initial release of altpg
- DB-API 2.0 compliant interface
- Basic Connection and Cursor classes
- Exception hierarchy (DatabaseError, IntegrityError, ProgrammingError, OperationalError, InterfaceError)
- Transaction management (commit, rollback)
- Connection context manager support
- Cursor context manager support
- Basic query execution with execute()
- Result fetching with fetchone(), fetchall(), fetchmany()
- SQLAlchemy dialect support
- Rust implementation using PyO3 and rust-postgres
- Comprehensive documentation and examples
- Basic test suite

### Known Limitations
- Parameter binding is simplified (not yet fully implemented)
- Result fetching returns empty results (requires caching implementation)
- No server-side cursors
- No COPY operations
- No async support
- No NOTIFY/LISTEN support
- Limited type adaptation

## Future Releases

### [0.2.0] - Planned
- Complete parameter binding implementation
- Result caching and proper fetch operations
- Improved type conversion
- Extended test suite with PostgreSQL integration tests

### [0.3.0] - Planned
- Server-side cursors
- COPY operations
- Connection pooling
- Performance optimizations

### [0.4.0] - Planned
- Async/await support
- NOTIFY/LISTEN support
- Full psycopg2/psycopg3 compatibility

[Unreleased]: https://github.com/manoelhc/altpg/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/manoelhc/altpg/releases/tag/v0.1.0
