# CI/CD Pipeline Setup

This document describes the comprehensive GitHub Actions CI/CD pipeline setup for the Fire & Forget AI Accounting project.

## 🚀 Overview

The CI/CD pipeline includes multiple workflows that ensure code quality, security, and reliability:

- **CI Pipeline**: Main testing and linting workflow
- **Test Matrix**: Multi-version testing across Python versions
- **Code Quality**: Pre-commit hooks and security scanning
- **Dependencies**: Automated dependency management
- **Coverage**: Code coverage reporting and tracking
- **Release**: Automated release management

## 📋 Workflows

### 1. CI Pipeline (`ci.yml`)

**Triggers**: Push to main/develop, Pull requests to main/develop

**Features**:
- Python 3.12 testing
- PostgreSQL and Redis services
- Comprehensive linting (ruff, black, isort, mypy, bandit, pip-audit)
- Full test suite execution
- Coverage reporting
- Security scanning

**Services**:
- PostgreSQL 15
- Redis 7

### 2. Test Matrix (`test-matrix.yml`)

**Triggers**: Push to main/develop, Pull requests to main/develop

**Features**:
- Multi-version testing (Python 3.11, 3.12)
- Unit and integration test separation
- Coverage reporting with Codecov integration
- Full service setup (PostgreSQL, Redis)

### 3. Code Quality (`quality.yml`)

**Triggers**: Push to main/develop, Pull requests to main/develop

**Features**:
- Pre-commit hook validation
- Security scanning (bandit, pip-audit)
- Dependency conflict detection
- Outdated package monitoring

### 4. Dependencies (`dependencies.yml`)

**Triggers**: Weekly schedule (Mondays 2 AM), Manual dispatch

**Features**:
- Weekly security audits
- Dependency conflict checking
- Outdated package detection
- Security report generation

### 5. Coverage (`coverage.yml`)

**Triggers**: Push to main/develop, Pull requests to main/develop

**Features**:
- Comprehensive coverage reporting
- Codecov integration
- HTML coverage report generation
- Coverage artifact uploads

### 6. Release (`release.yml`)

**Triggers**: Version tags (v*), Manual dispatch

**Features**:
- Automated package building
- Release creation
- Asset uploads
- Changelog generation

## 🛠️ Local Development

### Pre-commit Setup

Install pre-commit hooks for local development:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks on all files
pre-commit run --all-files
```

### Local CI Testing

Test the CI pipeline locally:

```bash
# Run full CI pipeline locally
make ci-local

# Or run individual components
make lint
make test
make format
```

### Available Make Commands

```bash
make help          # Show all available commands
make ci            # Run basic CI (lint + test)
make ci-local      # Run full CI pipeline locally
make lint          # Run all linting checks
make test          # Run tests
make test-cov      # Run tests with coverage
make format        # Format code
make clean         # Clean temporary files
```

## 🔧 Configuration Files

### Pre-commit Configuration (`.pre-commit-config.yaml`)

- **Trailing whitespace removal**
- **End-of-file fixing**
- **YAML/JSON/TOML validation**
- **Large file detection**
- **Merge conflict detection**
- **Debug statement detection**
- **Black code formatting**
- **isort import sorting**
- **Ruff linting with auto-fix**
- **MyPy type checking**
- **Bandit security scanning**
- **Flake8 code quality**

### Dependabot Configuration (`.github/dependabot.yml`)

- **Weekly Python dependency updates**
- **Weekly GitHub Actions updates**
- **Automated pull request creation**
- **Label and reviewer assignment**
- **Commit message standardization**

## 📊 Quality Gates

### Linting Requirements

- **Ruff**: No errors or warnings
- **Black**: Code properly formatted
- **isort**: Imports properly sorted
- **MyPy**: Strict type checking enabled
- **Bandit**: No security issues
- **pip-audit**: No vulnerable dependencies

### Testing Requirements

- **All tests must pass**
- **Coverage target**: 80%+ (configurable)
- **Unit tests**: Individual component testing
- **Integration tests**: End-to-end scenario testing
- **Performance tests**: Response time validation

### Security Requirements

- **No high-severity vulnerabilities**
- **Dependencies up to date**
- **Security scanning passed**
- **No hardcoded secrets**

## 🚦 Status Badges

The project includes status badges in the README:

```markdown
[![CI Pipeline](https://github.com/your-org/fnf-accounting/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/fnf-accounting/actions/workflows/ci.yml)
[![Code Quality](https://github.com/your-org/fnf-accounting/actions/workflows/quality.yml/badge.svg)](https://github.com/your-org/fnf-accounting/actions/workflows/quality.yml)
[![Test Matrix](https://github.com/your-org/fnf-accounting/actions/workflows/test-matrix.yml/badge.svg)](https://github.com/your-org/fnf-accounting/actions/workflows/test-matrix.yml)
[![Dependencies](https://github.com/your-org/fnf-accounting/actions/workflows/dependencies.yml/badge.svg)](https://github.com/your-org/fnf-accounting/actions/workflows/dependencies.yml)
```

## 🔄 Workflow Dependencies

### Service Dependencies

All workflows that require database access include:

```yaml
services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_PASSWORD: postgres
      POSTGRES_USER: postgres
      POSTGRES_DB: test_db
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
    ports:
      - 5432:5432

  redis:
    image: redis:7-alpine
    options: >-
      --health-cmd "redis-cli ping"
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
    ports:
      - 6379:6379
```

### Environment Variables

All workflows use consistent environment setup:

```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/test_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=test-secret-key-for-ci
OPENAI_API_KEY=test-key
USE_MOCK_DATA=true
```

## 📈 Monitoring and Reporting

### Coverage Tracking

- **Codecov integration** for coverage tracking
- **HTML coverage reports** for detailed analysis
- **Coverage thresholds** enforcement
- **Trend analysis** over time

### Security Monitoring

- **Weekly security scans** via Dependabot
- **Vulnerability reporting** with severity levels
- **Automated dependency updates**
- **Security audit reports**

### Performance Monitoring

- **Test execution time** tracking
- **Build time** optimization
- **Resource usage** monitoring
- **Performance regression** detection

## 🚀 Deployment Integration

### Release Process

1. **Version tagging** triggers release workflow
2. **Automated testing** ensures quality
3. **Package building** creates distributables
4. **Release creation** with changelog
5. **Asset upload** for distribution

### Environment Promotion

- **Development**: All PRs and pushes to develop
- **Staging**: Merges to main branch
- **Production**: Version tags and releases

## 🔧 Troubleshooting

### Common Issues

1. **Service startup failures**: Check health check configurations
2. **Dependency conflicts**: Review requirements.txt
3. **Test failures**: Check environment variables and service connectivity
4. **Linting errors**: Run `make format` to auto-fix issues

### Debug Commands

```bash
# Check service health
docker-compose ps

# Run specific tests
pytest tests/unit/test_specific.py -v

# Check linting issues
ruff check src tests --verbose

# Run type checking
mypy src --verbose
```

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [Codecov Documentation](https://docs.codecov.com/)

## 🎯 Next Steps

1. **Update repository URLs** in workflow files
2. **Configure Codecov** for coverage tracking
3. **Set up branch protection** rules
4. **Configure required status checks**
5. **Test workflows** with sample PRs
6. **Monitor performance** and optimize as needed
