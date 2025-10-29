# Contributing to Agentic Auth Prototype

Thank you for your interest in contributing! This project welcomes improvements, bug fixes, and extensions.

## How to Contribute

### Reporting Issues

1. Check existing issues to avoid duplicates
2. Provide detailed reproduction steps
3. Include environment details (OS, Docker version)
4. Share relevant logs or error messages

### Submitting Changes

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitLab
   git clone https://gitlab.com/YOUR_USERNAME/agentic-auth-prototype.git
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow existing code style
   - Add tests if applicable
   - Update documentation

4. **Test your changes**
   ```bash
   docker compose up --build
   # Verify experiments run successfully
   ```

5. **Commit with clear messages**
   ```bash
   git commit -m "Add feature: brief description"
   ```

6. **Push and create merge request**
   ```bash
   git push origin feature/your-feature-name
   # Create merge request on GitLab
   ```

## Development Guidelines

### Code Style

**Python:**
- Follow PEP 8
- Use type hints where helpful
- Add docstrings for functions

**Docker:**
- Pin specific versions
- Use multi-stage builds where appropriate
- Document build arguments

### Testing

Before submitting:
- [ ] All services build successfully
- [ ] Experiments run without errors
- [ ] Results are reproducible
- [ ] Documentation is updated

### Documentation

Update relevant docs:
- `README.md`: Major features or architecture changes
- `CHANGELOG.md`: All user-facing changes
- Code comments: Complex logic
- Configuration examples: New options

## Areas for Contribution

### High Priority

- **SPIFFE/SPIRE integration**: Implement full Pattern 3
- **TLS support**: Production-ready security
- **Distributed JTI cache**: Redis integration
- **Performance testing**: High-concurrency scenarios
- **CI/CD improvements**: Automated testing

### Medium Priority

- **Additional patterns**: Patterns 1, 4, 5 implementations
- **Multi-hop delegation**: Complex agent hierarchies
- **Monitoring/observability**: Metrics and dashboards
- **Configuration examples**: Production deployment guides

### Good First Issues

- **Documentation improvements**: Typos, clarity
- **Error handling**: Better error messages
- **Logging**: Structured logging
- **Examples**: Additional use cases

## Code Review Process

1. Automated CI/CD checks must pass
2. At least one maintainer approval required
3. Address review comments
4. Squash commits before merge

## Questions?

- Open a discussion issue on GitLab
- Email maintainers (see README.md)
- Check existing documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
