# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-24

### Added
- Initial release of authentication prototype
- OAuth 2.0 client credentials implementation
- RFC 8693 Token Exchange support with Keycloak 26.2
- RFC 9449 DPoP implementation with ECDSA P-256
- JTI-based replay prevention with in-memory cache
- Comprehensive measurement and analysis scripts
- Docker Compose orchestration for all services
- Automated experiment runner (cold/warm path testing)
- Statistical analysis and LaTeX table generation
- Complete documentation and setup guides

### Validated
- Cold-path latency: 52.22ms ±8.08ms (n=20)
- Warm-path latency: 11.32ms ±4.22ms (n=100)
- Caching speedup: 4.6× improvement
- DPoP replay prevention: HTTP 403 on duplicate JTI
- Token Exchange: Native Keycloak RFC 8693 support

### Known Limitations
- HTTP only (no TLS) - for research purposes
- In-memory JTI cache (not distributed)
- Default credentials (not production-hardened)
- Single-host deployment (no scalability testing)
- Pattern 3 only (other patterns not implemented)

## [Unreleased]

### Planned Features
- SPIFFE/SPIRE integration for Pattern 2
- Multi-hop delegation testing
- Distributed JTI cache (Redis)
- TLS support for production deployment
- Performance benchmarks under high concurrency
- Additional pattern implementations
