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

## Development Commands

### Testing
```bash
# Run all tests
pytest test_prodict.py

# Run specific test
pytest test_prodict.py::TestProdict::test_deep_recursion_from_dict

# Run with verbose output
pytest -v test_prodict.py
```

### Linting
```bash
# Install flake8
pip install flake8

# Check for critical errors
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Full lint (warnings only)
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

### Building and Distribution
```bash
# Build distribution
python setup.py sdist

# Check distribution with twine
pip install twine
twine check dist/*

# Test upload (requires credentials)
twine upload --repository testpypi dist/*
```

### Installation
```bash
# Install locally for development
pip install -e .

# Install from source
pip install .
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

## Version and Compatibility

- Current version: 0.8.20
- Requires Python 3.7+ (uses `__annotations__`)
- Setup uses distutils.core (setup.py) and Poetry (pyproject.toml)
- No runtime dependencies

## CI/CD

GitHub Actions workflow (.github/workflows/pythonapp.yml):
- Runs on every push
- Test job: flake8 linting, pytest, twine check
- Deploy job: Runs on master branch, uploads to TestPyPI and PyPI (requires secrets)
