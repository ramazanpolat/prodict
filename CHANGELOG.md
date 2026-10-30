# Changelog

All notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow the numbers
published on [PyPI](https://pypi.org/project/prodict/#history).

## [Unreleased]

### Added

- `from_dict()` is typed to return the class it is called on, so an IDE completes the
  fields of `Model.from_dict(...)`.
- `del p.key` deletes a key, and `dir(p)` lists the keys that are identifiers, so a REPL
  or notebook can complete them.
- Issue forms for bug reports and feature requests, a pull request template, and
  `SECURITY.md`, which points to GitHub's private vulnerability reporting.

### Changed

- A value that cannot be converted to its annotation (`'abc'` for an `int`) is stored as
  given instead of raising `ValueError`. Annotations are a convenience, not validation.
- A subclass of a model has the annotations of its base classes: their values are
  converted and they start as `None`. Before, a subclass lost them on Python 3.10+, and
  on 3.8 and 3.9 when it declared annotations of its own.
- A Prodict assigned to an attribute annotated with its class, a base class, `dict` or
  `List[...]` of its class is stored as it is, not copied.
- `List[dict]` items become `Prodict` instances, like a `dict` attribute, instead of
  plain dict copies.
- A Prodict assigned to an unannotated attribute, or passed in as data, is stored as it
  is, not copied.
- `from_dict(d)` is `cls(d)` (still `cls(**d)` when a subclass's own `__init__` accepts
  the data as keyword arguments): a positional dict, keyword arguments and `from_dict()`
  are treated the same way.
- A dict that contains itself becomes a Prodict that contains itself, instead of raising
  `RecursionError`.
- A nested model whose constructor raises keeps its dict as given, like any other value
  that cannot be converted.
- `copy`, `copy.deepcopy()` and `pickle` restore the data as it is stored: `init()` does
  not run again and values are not converted again. Instance attributes and slots are
  kept.
- Names of the form `__name__` are never looked up as keys by attribute access, so a key
  such as `__deepcopy__` cannot stand in for a Python protocol hook; read it with
  brackets.
- `ClassVar` annotations are left out of the model: they no longer appear in every
  instance as `None`.
- `Annotated[T, ...]` annotations convert as `T`.
- The internal `get_constructor()` method is gone; `set_attribute()` converts values.

### Fixed

- `Optional[T]`, `Union[T, None]` and `T | None` annotations convert values as `T`,
  instead of storing them unconverted or, on Python 3.14+, raising `AttributeError`
  ([#38](https://github.com/ramazanpolat/prodict/issues/38)). Unions of several types store
  values as given instead of raising `AttributeError` on Python 3.14+.
- The built-in generics `list[T]`, `tuple[...]` and `dict[K, V]` work like `List[T]`,
  `Tuple[...]` and `Dict[K, V]` instead of raising `KeyError` or `TypeError`
  ([#21](https://github.com/ramazanpolat/prodict/issues/21)).
- `List[Any]`, `List[Optional[T]]` and other lists of non-class types no longer raise
  `TypeError`.
- Keys named like `dict` methods (`items`, `keys`, `pop`, ...) and keys that are not
  strings work in `from_dict()`, the constructor, `copy`, `copy.deepcopy()` and `pickle`,
  at any depth, instead of raising `TypeError`.
- Nested dicts passed positionally (`Prodict({'a': {'b': 1}})`) become Prodicts, as with
  `from_dict()` ([#42](https://github.com/ramazanpolat/prodict/issues/42)).
- `copy.deepcopy()` and `pickle` handle a Prodict that contains itself, and keep shared
  values shared, instead of raising `RecursionError`.
- String annotations, including `from __future__ import annotations`, convert values. An
  annotation that cannot be resolved stores values as given instead of raising
  `TypeError` for dicts, and does not stop the model's other annotations from converting.
- A dict passed positionally (`Model({...})`) no longer loses the values of annotated
  attributes; they are converted like keyword arguments, which still take precedence
  ([#55](https://github.com/ramazanpolat/prodict/issues/55)).
- Assigning a Prodict to an attribute annotated with `dict`, `bool`, `tuple`, `List[T]`
  or `Tuple[...]` no longer raises `AttributeError`, so `copy.deepcopy()` works on models
  with a `dict` attribute ([#56](https://github.com/ramazanpolat/prodict/issues/56)).
- `typing.Dict` and `Dict[K, V]` annotations accept dict values and convert them to
  `Prodict` like `dict` does, instead of raising `TypeError`
  ([#57](https://github.com/ramazanpolat/prodict/issues/57)).

## [0.8.23] - 2026-10-27

The library code is unchanged from 0.8.22. This release publishes corrected package
metadata (supported Python versions, license, project links) and the new README to PyPI.

### Added

- Documentation in `docs/`: a tutorial and guides for typed models, serialization,
  development and releasing. Their code samples run as doctests.
- Runnable examples in `examples/`, from the basics to a complete JSON API client, each
  with a README. CI runs them on every supported Python version.
- `CHANGELOG.md`, `CONTRIBUTING.md` and `AGENTS.md`.

### Changed

- CI tests Python 3.8 through 3.15 with uv-managed interpreters; classifiers list exactly
  those versions.
- Publishing happens only when `pyproject.toml` carries a version PyPI does not have yet.
  PyPI tokens reach twine through environment variables and are never written to disk or
  printed.
- Package metadata: SPDX license expression (`MIT`), project URLs for documentation and
  changelog, clearer description and keywords.
- The `dev` extra became a `dev` dependency group (`uv run pytest`, or
  `pip install --group dev`).
- `README.MD` renamed to `README.md` and rewritten; images moved to `docs/images/`.

### Removed

- Python 3.7 support: `requires-python` is now `>=3.8`. 3.7 is not in the CI matrix (uv
  has no 3.7 interpreters), and the build backend now requires `hatchling>=1.27`, which
  needs Python 3.8. pip on Python 3.7 keeps resolving to 0.8.22, which has the same
  library code.
- Leftovers of the old setuptools build: `MANIFEST`, `MANIFEST.in`, `README.txt`, `.pypirc`.
- `examples.py`, replaced by `examples/`.

## [0.8.22] - 2025-10-14

### Changed

- Packaging moved to `pyproject.toml` with the hatchling build backend; `setup.py`,
  `setup.cfg` and `requirements.txt` removed (#52). First release with a wheel on PyPI.
- CI builds and publishes with uv.

## [0.8.21] - 2025-10-13

### Added

- `to_dict(convert_list_items=True)` converts Prodict items in lists to dicts while
  respecting `exclude_none` (#51).

### Fixed

- `to_dict()` passes `exclude_none_in_lists` down to nested Prodicts (#44).

## [0.8.20] - 2024-11-18

### Fixed

- Package metadata fixes (#49); the MIT license is declared in the package metadata (#33).

### Changed

- Source formatted with black to avoid long lines (#29).

## [0.8.19] - 2024-11-18

### Fixed

- A missing attribute raises `AttributeError` instead of `KeyError`, so `getattr()` with
  a default and `hasattr()` work (#47, #48).

## Earlier releases

Versions 0.7 to 0.8.18 (2018 to 2021) are listed in the
[PyPI release history](https://pypi.org/project/prodict/#history). Earlier versions exist
only as git tags (`v0.1` to `v0.6`).

[Unreleased]: https://github.com/ramazanpolat/prodict/compare/v0.8.23...HEAD
[0.8.23]: https://pypi.org/project/prodict/0.8.23/
[0.8.22]: https://pypi.org/project/prodict/0.8.22/
[0.8.21]: https://pypi.org/project/prodict/0.8.21/
[0.8.20]: https://pypi.org/project/prodict/0.8.20/
[0.8.19]: https://pypi.org/project/prodict/0.8.19/
