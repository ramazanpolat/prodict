# Changelog

All notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow the numbers
published on [PyPI](https://pypi.org/project/prodict/#history).

## [Unreleased]

### Added

- Issue forms for bug reports and feature requests, a pull request template, and
  `SECURITY.md`, which points to GitHub's private vulnerability reporting.

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
