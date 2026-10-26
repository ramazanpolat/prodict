# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Prodict** is a Python library that extends `dict` to support dot-accessible attributes with IDE-friendly auto-completion and automatic type conversion. It inherits from `dict` while adding type annotations, nested object instantiation, and dynamic attribute access.

## Core Architecture

### Main Components

**prodict/__init__.py** - Single-file implementation containing:
- `Prodict` class: Main class extending `dict` with dot notation and type conversion
- `GenericMeta`: Metaclass for generic type handling
- Type conversion logic for annotated attributes (int, str, float, bool, list, tuple, List[T])
- Automatic nested Prodict instantiation for dict values
- Reserved key handling (DICT_RESERVED_KEYS prevents shadowing dict methods)

### Key Design Patterns

1. **Attribute Access**: `__getattr__` and `__setattr__` map attribute access to dict operations
2. **Type Conversion**: `set_attribute()` uses `get_constructor()` to auto-convert types based on type annotations
3. **Nested Instantiation**: Dict values automatically become Prodict instances; List[CustomProdict] elements auto-instantiate as CustomProdict
4. **UUID Self Parameter**: Uses `self_d921dfa9_4e93_4123_893d_a7e7eb783a32` in `__init__` and `set_attributes` to avoid conflicts when dict keys are named "self" (see test_issue15)
5. **init() Hook**: Provides `init()` method (not `__init__`) for setting defaults without calling super()

### Type System

- Annotated attributes undergo automatic type conversion (e.g., `user_id: int` converts "1" to 1)
- `Any` type annotation disables conversion while preserving IDE auto-completion
- Unannotated dict values automatically become Prodict instances
- `List[CustomProdict]` automatically instantiates list elements as CustomProdict objects

### to_dict() Method

The `to_dict()` method supports flexible serialization with four parameters:

- **is_recursive**: When True, converts nested Prodict attributes to plain dicts
- **exclude_none**: When True, excludes top-level key-value pairs where value is None
- **exclude_none_in_lists**: When True, converts list items to dicts and excludes None values (legacy)
- **convert_list_items**: When True, converts Prodict items in lists to dicts (respects exclude_none)

**Key difference**: `convert_list_items=True` with `exclude_none=False` allows converting list items to dicts while keeping None values, which was previously impossible.

## Development Commands

This project uses **uv** for modern Python package management.

### Setup and Installation

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install package in development mode with dev dependencies
uv pip install -e ".[dev]"

# Or install just the package
uv pip install -e .
```

### Testing

```bash
# Run all tests
uv run --extra dev pytest test_prodict.py

# Run specific test
uv run --extra dev pytest test_prodict.py::TestProdict::test_dict_value_all_combinations

# Run with verbose output
uv run --extra dev pytest -v test_prodict.py
```

### Building and Distribution

```bash
# Build distribution packages
uv build

# Check package metadata
uv pip show prodict
```

### Development Workflow

```bash
# Create a virtual environment (optional, uv manages this)
uv venv

# Activate virtual environment
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows

# Install in editable mode
uv pip install -e ".[dev]"

# Run tests
uv run --extra dev pytest
```

## Testing Guidelines

### Test Structure
- All tests in `test_prodict.py` using unittest.TestCase
- Test classes define Prodict subclasses (Computer, Ram, Cpu, etc.) to verify nested instantiation
- Key test scenarios: type conversion, nested objects, List[T] handling, deep recursion, serialization (pickle), to_dict() options

### Critical Test Cases
- **test_deep_recursion_from_dict**: Validates nested Prodict/List[Prodict] instantiation
- **test_issue15**: Ensures "self" can be used as a key name (validates UUID self parameter)
- **test_issue18**: Verifies generator expressions work in constructor
- **test_to_dict_exclude_none**: Tests exclude_none and exclude_none_in_lists parameters
- **test_convert_list_items_parameter**: Tests the new convert_list_items parameter
- **test_deepcopy1/2**: Validates copy.deepcopy() preserves type and creates new instances

## Important Implementation Details

### Reserved Names
- Cannot use dict method names as attributes (keys(), values(), items(), etc.)
- DICT_RESERVED_KEYS contains all reserved names from vars(dict).keys()

### Type Conversion Behavior
- Only applies to annotated attributes
- Built-in types (int, str, float, bool, list, tuple) auto-convert
- dict types always convert to Prodict (unless annotated as dict)
- List[CustomProdict] elements instantiate as CustomProdict using from_dict()

### Class vs Instance Attributes
- Prodict only works with instance attributes
- Setting a class attribute via dot notation creates a shadowing instance attribute
- Access shadowed attributes via `.get('attr_name')` or set class attributes via ClassName.attr

## Package Management

This project uses **uv** and follows modern Python packaging standards:

- **pyproject.toml**: PEP 621 compliant project metadata and build configuration
- **hatchling**: Build backend for creating wheels and sdists
- No setup.py, setup.cfg, or requirements.txt (all managed via pyproject.toml)

### Version and Compatibility

- Current version: 0.8.22
- Requires Python 3.7+ (CI tests 3.8 through 3.15; uv has no 3.7 builds)
- No runtime dependencies
- Development dependencies: pytest>=7.0.0

### Publishing

```bash
# Build the package
uv build

# Upload to PyPI (requires credentials)
twine upload dist/*
```

## CI/CD

GitHub Actions workflow (.github/workflows/pythonapp.yml):
- Runs on every push
- Test job: pytest on a Python 3.8-3.15 matrix (uv-managed interpreters)
- Build job: flake8 linting, `uv build`, twine check
- Deploy job: Runs on master branch after both. It publishes only when the `version` in pyproject.toml is not on PyPI yet, so a push without a version bump uploads nothing. Tokens come from the `TESTPYPI_TOKEN` / `PYPI_TOKEN` secrets through `TWINE_PASSWORD` and are never written to disk
- Adding a Python version: add it to the workflow matrix and to the `classifiers` in pyproject.toml together
