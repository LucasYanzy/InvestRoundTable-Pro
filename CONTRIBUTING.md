# Contributing to Investment Masters Roundtable

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## 🚀 Getting Started

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/your-username/investment-masters-roundtable.git`
3. **Install dependencies**: `pip install -r requirements.txt && pip install ruff pytest`
4. **Create a branch**: `git checkout -b feature/your-feature-name`

## 📋 Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install ruff pytest

# Run smoke tests
python -m pytest tests/test_smoke.py -v

# Run linter
ruff check .

# Fix lint issues automatically
ruff check --fix .
```

## 🤖 Adding a New Master

One of the most impactful contributions is adding a new investment master. Here's how:

### Stage 1 (Investment Master)
1. Create a skill framework file: `masters/skill_references/investment_masters/new-master-perspective.md`
2. Add the master entry to `masters/registry.py` → `STAGE1_MASTERS`
3. Update `config.py` → `STAGE1_COUNT`
4. Update the master tables in both `README.md` and `README_CN.md`

### Stage 2 (Technical Master)
1. Create: `masters/skill_references/technical_masters/new-master-perspective.md`
2. Add to `masters/registry.py` → `STAGE2_MASTERS`
3. Update `config.py` → `STAGE2_COUNT`

### Stage 3 (Signal Master)
1. Create: `masters/skill_references/signal_masters/new-master-signal-perspective.md`
2. Add to `masters/registry.py` → `STAGE3_MASTERS` (include `indicator_keys`)
3. Update `config.py` → `STAGE3_COUNT`

### Skill Framework File Guidelines
- Minimum 3KB for signal masters, 8KB for investment/technical masters
- Include specific decision rules, thresholds, and examples
- Cover multi-market adaptations (US / China / HK) if applicable
- Use Markdown format with clear section headers

## 💻 Code Style

- **Formatter & Linter**: We use [ruff](https://docs.astral.sh/ruff/)
- **Line length**: 120 characters max
- **Python version**: 3.9+ compatible
- **Type hints**: Encouraged but not strictly required
- **Docstrings**: Required for all public functions and classes
- **Comments**: In Chinese or English — both are welcome

## 📝 Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new technical master (Fibonacci)
fix: handle empty DataFrame in fetcher
docs: update architecture diagram
refactor: simplify signal conflict detection
test: add unit tests for stage3 aggregation
```

## 🔀 Pull Request Process

1. Ensure all smoke tests pass: `python -m pytest tests/test_smoke.py -v`
2. Ensure linting passes: `ruff check .`
3. Update documentation if you've changed APIs or added features
4. Fill out the PR template with a clear description
5. Request review from maintainers

## 🐛 Bug Reports

When filing a bug report, please include:
- Python version and OS
- Steps to reproduce
- Expected vs. actual behavior
- Error logs (with `--verbose` flag)

## 📄 License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
