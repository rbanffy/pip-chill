# pip-chill Context for AI Assistants

## Project Overview

**pip-chill** is a Python CLI tool that generates requirements files listing only top-level packages (those not required as dependencies by other listed packages). Unlike `pip freeze`, it filters out transitive dependencies, creating cleaner, more accurate requirements files.

**Key Value**: Distinguishes between packages developers care about vs. implicit dependencies, reducing requirements bloat.

## Critical Constraint: Zero External Dependencies

⚠️ **pip-chill must have no dependencies outside the Python standard library.** This is a core design principle and non-negotiable. Any contribution, feature, or bugfix must:
- Use only stdlib modules (e.g., `importlib.metadata`, `argparse`, `re`, `typing`)
- Never introduce third-party imports
- Maintain the lean, self-contained nature of the tool

This constraint ensures pip-chill remains lightweight, fast, and free from dependency conflicts.

## Key Files & Architecture

### Core Files
- **`pip_chill/pip_chill.py`** - Core engine
  - `Distribution` class: Wraps package metadata with dependency tracking
  - `chill()` function: Main algorithm that identifies top-level packages
  - Uses `importlib.metadata` to query installed packages

- **`pip_chill/cli.py`** - Command-line interface
  - Entry point via `pip-chill` console script
  - Argument parsing: `--no-version`, `--no-chill`, `--all`, `--verbose`
  - Delegates core logic to `pip_chill.chill()`

- **`pip_chill/__init__.py`** - Module exports
  - Exports `chill` function for programmatic use

- **`tests/test_pip_chill.py`** - Test suite
  - Unit and integration tests for Distribution class and chill() function

## Programming Guidelines

### Code Style
- **Python Version**: 3.10+
- **Type Hints**: Use comprehensive type hints (e.g., `Set[Any]`, `bool`)
- **Docstrings**: Triple-quoted module/class/function docstrings explaining purpose
- **Naming**: Clear, descriptive names. Classes use CamelCase, functions/vars use snake_case
- **No External Dependencies**: Keep the project lightweight (zero production dependencies as of v1.0.5)

### Key Patterns
- Use `importlib.metadata` for querying installed packages (not subprocess calls)
- Represent package relationships via the `Distribution` class with `required_by` set tracking
- Return tuples: (distributions, dependencies) — separate views for different use cases
- Use `argparse` for CLI argument handling

## Architectural Guidelines

### Separation of Concerns
- **CLI Layer** (`cli.py`): Handles I/O and argument parsing only
- **Core Logic** (`pip_chill.py`): Pure algorithm for identifying top-level packages
- **Module API** (`__init__.py`): Clean exports for library users

### Data Flow
1. Query installed packages via `importlib.metadata`
2. Build dependency graph (each package knows who requires it)
3. Identify top-level packages (those not required by anything)
4. Format output (version control via `hide_version` flag)
5. CLI prints or library returns results

### Distribution Class
- Immutable-by-design: no setters, initialization via `__init__`
- Comparison operators use package name only (`__eq__`, `__lt__`)
- Hashable for use in sets/dicts
- String representation shows dependencies when present

## Style Conventions

### Formatting
- **Indentation**: 4 spaces (PEP 8)
- **Line Length**: Reasonable limits, break long argument lists
- **Imports**: Group standard library, third-party, local (already zero third-party)

### String Handling
- Use f-strings for formatting
- Use regex (`re.compile`) for parsing requirement strings (see `pattern` in pip_chill.py)

### Error Handling
- Presently minimal error handling; packages are expected to be query-able
- Future improvements: handle missing metadata gracefully

### Testing
- Write unit tests in `tests/test_pip_chill.py`
- **Avoid mocking entirely** — mocking is a strong code smell indicating the need for refactoring
- Separate functionality into parts with no environmental dependencies that would require mocks
- If you find yourself needing to mock `importlib.metadata` or other stdlib, refactor to inject dependencies or separate concerns instead
- Test both happy paths and edge cases (circular deps, version formats, etc.)

## When Contributing

1. **Maintain zero external dependencies** — any change should not introduce new imports beyond stdlib
2. **Preserve CLI backward compatibility** — existing flags and output format are part of the API
3. **Keep the Distribution class clean** — it's the core data structure
4. **Add tests for new features** — especially around dependency resolution
5. **Use type hints** — all new functions should include type annotations
6. **Document intent** — docstrings for non-trivial logic

## Notes for AI Assistants

- This is a mature, stable tool (v1.0.5, "Production/Stable" status)
- The primary use case is Unix-like systems, but it's platform-independent
- The package is self-aware: can hide itself from output with `--no-chill` flag
- Verbose mode includes commented dependencies for transparency
