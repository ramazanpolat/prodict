# AGENTS.md

Instructions for coding agents (and humans) working in this repository: what the project
is, how to install and run it, how it is tested, and how it is released.

## Project

`prodict` is a single-module Python library: `Prodict`, a `dict` subclass whose keys are
also attributes, with type conversion driven by class annotations. It has no runtime
dependencies. `requires-python` is `>=3.8`; CI tests 3.8 through 3.15. On Python 3.7,
pip resolves to 0.8.22, the last version that declares 3.7 support.

| Path | What |
|---|---|
| `prodict/__init__.py` | The whole library. |
| `test_prodict.py` | Unit tests (`unittest.TestCase`, run with pytest). |
| `docs/` | Tutorial and guides. Every `>>>` block is a doctest. |
| `examples/NN-name/` | Runnable `main.py` plus a README showing its exact output. |
| `pyproject.toml` | Metadata, hatchling build, `dev` dependency group, pytest config. |
| `.github/workflows/pythonapp.yml` | CI: `test` matrix, `build`, `deploy`. |
| `CHANGELOG.md` | Keep a Changelog format; new entries go under `Unreleased`. |

## Install and run

Requires [uv](https://docs.astral.sh/uv/). No other setup:

```bash
uv run pytest                                        # unit tests + doctests in docs/
for e in examples/*/main.py; do uv run python "$e"; done
uv run --python 3.8 pytest                           # any other supported version
uvx flake8 . --select=E9,F63,F7,F82                  # the lint CI enforces
uv build && uvx twine check dist/*                   # sdist + wheel
```

Without uv: `pip install -e . --group dev` (pip 25.1+, Python 3.9+; on 3.8
`pip install -e . 'pytest>=7'`), then `pytest`.

## Rules for changes

- **Keep docs true.** Behavior changes must update `docs/` (doctests fail otherwise) and
  any affected `examples/` README, whose output block must match `main.py` exactly.
- **Stay compatible with Python 3.8 syntax** in the library, tests, docs and examples:
  `typing.List` rather than `list[int]`, no `X | Y` unions, no `match`.
- **Do not change `version`** in `pyproject.toml` unless the change is a release (see
  below); a version bump merged to `master` publishes to PyPI.
- **Add a changelog line** under `Unreleased` for anything a user would notice.
- **Never commit credentials.** PyPI tokens live only in the repository secrets.

## How the library works

- `Prodict.__init__` calls `dict.__init__` with all arguments, sets every annotated
  attribute to `None`, calls the `init()` hook (where subclasses set defaults), then
  applies the keyword arguments again through `set_attributes()`, which converts them.
  Values for annotated keys passed in a positional dict are therefore lost (reset to
  `None`); `from_dict()` passes keywords and is not affected.
- `__getattr__` / `__setattr__` map attributes to keys. A missing key raises
  `AttributeError`.
- `set_attribute()` converts values for annotated attributes via `get_constructor()`:
  `int`, `float`, `str`, `list`, `List[T]` (item-wise), `Tuple[...]` (to `tuple`),
  `Prodict` and its subclasses (`from_dict`), and `Any` (no conversion). A bare `dict`
  annotation converts plain dicts but raises `AttributeError` for Prodict values and in
  `copy.deepcopy`, because `get_constructor()` checks `isinstance(value, Prodict)` first. `bool`,
  plain `tuple` and other types are stored unconverted (a Prodict value raises
  `AttributeError`). `None` is never converted.
  `p['key'] = ...` and `update()` are plain dict operations and bypass conversion.
- Unannotated dict values become `Prodict` instances.
- Names of `dict` methods (`DICT_RESERVED_KEYS`) cannot be set as attributes (`TypeError`).
- `__init__` and `set_attributes` name their first parameter
  `self_d921dfa9_4e93_4123_893d_a7e7eb783a32` so that `self` works as a key
  (`test_issue15`). Keep it that way.
- `to_dict()` options: `is_recursive`, `exclude_none`, `convert_list_items`,
  `exclude_none_in_lists` (legacy). See `docs/guides/serialization.md`.

Known limitations, documented in `docs/guides/typed-models.md`: `Optional`/`Union`
annotations are unsupported (unconverted or an error, depending on value and Python
version; on 3.14+ every non-`None` value fails), `Dict[K, V]` raises
`TypeError` for dict values, a bare `dict` annotation breaks on Prodict values and
`deepcopy`, built-in generics (`list[int]`) fail for most values (`KeyError`, `TypeError`
or `AttributeError` depending on the value), and positional dicts lose
annotated values.

## CI

`.github/workflows/pythonapp.yml` runs on pull requests (including from forks) and on pushes
to `master`:

- `test`: for each Python 3.8-3.15, `uv run --managed-python pytest`, then every example.
- `build`: flake8 (errors fail, the rest is reported), `uv build`, `twine check`.
- `deploy` (only on a push to `master`, after both): builds, then checks PyPI for the version in
  `pyproject.toml`. If it is new, uploads to TestPyPI and then PyPI with tokens from the
  `TESTPYPI_TOKEN` / `PYPI_TOKEN` secrets via `TWINE_PASSWORD`. If it exists, it stops.

## Releasing

Follow `docs/guides/releasing.md`: bump `version`, move `Unreleased` entries in
`CHANGELOG.md` under the new version, merge to `master`, let `deploy` publish, then tag
`vX.Y.Z`. A release needs the maintainer's approval; agents prepare it, they do not merge
it on their own.
