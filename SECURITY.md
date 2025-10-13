# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in altpg, please report it by:

1. **DO NOT** open a public GitHub issue
2. Email the maintainer at: [Create a private security advisory](https://github.com/manoelhc/altpg/security/advisories/new)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will acknowledge your email within 48 hours and provide a detailed response within 7 days.

## Security Best Practices

When using altpg:

1. **Never commit credentials** - Use environment variables or secure credential management
2. **Use parameterized queries** - Always use parameter binding to prevent SQL injection
3. **Keep dependencies updated** - Regularly update altpg and PostgreSQL
4. **Use SSL/TLS connections** - Enable SSL for production databases
5. **Limit database privileges** - Use least-privilege principle for database users
6. **Validate input** - Always validate and sanitize user input before using in queries
7. **Monitor connections** - Use connection pooling and monitor for anomalies
8. **Audit access** - Keep logs of database access and modifications

## Known Security Considerations

- This is an early-stage project (v0.1.x) and may not have undergone comprehensive security audits
- Parameter binding implementation is still being enhanced
- Error messages may contain sensitive information - be careful in production logging

## Disclosure Policy

When a security vulnerability is reported:

1. We will confirm receipt within 48 hours
2. We will investigate and provide a timeline for fixes
3. We will release a patch as soon as possible
4. We will publish a security advisory after the fix is released
5. We will credit the reporter (unless they wish to remain anonymous)

## Security Updates

Security updates will be:

- Released as patch versions (e.g., 0.1.1)
- Announced in CHANGELOG.md
- Tagged as security updates in releases
- Communicated via GitHub security advisories

## Contact

For security-related questions or concerns:
- GitHub Security Advisories: [Create Advisory](https://github.com/manoelhc/altpg/security/advisories/new)
- General questions: [Open an Issue](https://github.com/manoelhc/altpg/issues)
