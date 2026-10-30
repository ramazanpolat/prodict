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
| `docs/` | Tutorial and guides. Every `>>>` block is a doctest, as in `README.md`. |
| `examples/NN-name/` | Runnable `main.py` plus a README showing its exact output. |
| `pyproject.toml` | Metadata, hatchling build, `dev` dependency group, pytest config. |
| `.github/workflows/pythonapp.yml` | CI: `test` matrix, `build`, `deploy`. |
| `CHANGELOG.md` | Keep a Changelog format; new entries go under `Unreleased`. |

## Install and run

Requires [uv](https://docs.astral.sh/uv/). No other setup:

```bash
uv run pytest                                        # unit tests + doctests in docs/ and README.md
for e in examples/*/main.py; do uv run python "$e"; done
uv run --python 3.8 pytest                           # any other supported version
uvx flake8 . --select=E9,F63,F7,F82                  # the lint CI enforces
uv build && uvx twine check dist/*                   # sdist + wheel
```

Without uv: `pip install -e . --group dev` (pip 25.1+, Python 3.9+; on 3.8
`pip install -e . 'pytest>=7'`), then `pytest`.

## Rules for changes

- **Keep docs true.** Behavior changes must update `docs/` and `README.md` (doctests fail
  otherwise) and any affected `examples/` README, whose output block must match `main.py`
  exactly.
- **Stay compatible with Python 3.8 syntax** in the library, tests, docs and examples:
  `typing.List` rather than `list[int]`, no `X | Y` unions, no `match`.
- **Do not change `version`** in `pyproject.toml` unless the change is a release (see
  below); a version bump merged to `master` publishes to PyPI.
- **Add a changelog line** under `Unreleased` for anything a user would notice.
- **Never commit credentials.** PyPI tokens live only in the repository secrets.

## How the library works

- `Prodict.__init__` calls `dict.__init__` with all arguments, reads back the data that
  came in positionally, sets every annotated attribute to `None`, calls the `init()` hook
  (where subclasses set defaults), then stores the positional data and the keyword
  arguments again through `_store()`, which converts them. Keyword arguments win.
  `from_dict(d)` is `cls(d)`, or `cls(**d)` when a subclass's own `__init__` accepts the
  data as keyword arguments (`_takes_keywords` binds it to the signature); it is typed to
  return `cls`. A thread-local memo (`_converting`, keyed by the source dict's id) maps
  each dict that `Prodict(d)` converts to its instance, so cyclic and shared dicts stay
  cyclic and shared for models with the default constructor. `init()` runs outside the
  memo, so defaults are never shared, and a failed instance is removed from it.
- `__getattr__` / `__setattr__` / `__delattr__` map attributes to keys. A missing key
  raises `AttributeError`, and so does any `__dunder__` name (`_is_dunder`), so that
  protocol lookups (`copy.deepcopy` asks for `__deepcopy__`) never get data.
  `__delattr__` deletes an instance attribute or a deletable descriptor before a key.
  `__dir__` adds the keys that are identifiers and not dunder names.
- `attr_types()` returns the annotations of the class and its base classes, via
  `typing.get_type_hints()`, without `ClassVar` ones. If that fails, each annotation is
  resolved on its own (`_resolve`, same name lookup order) and the ones that cannot be keep
  their raw form (`annotationlib` on 3.14+); later calls retry them, so a forward reference
  converts once its class exists. The result is stored on the class itself, under a name
  that is not an identifier, and written under a lock. `has_attr()` is
  `name in attr_types()`.
- `_store()` (used by the constructor and `set_attribute()`) converts values for
  annotated attributes with `_convert(annotation, value)`: `int`, `float`, `str`, `list`;
  `List[T]` / `list[T]` (item-wise); `Tuple[...]` / `tuple[...]` (to `tuple`); `dict` / `Dict[K, V]` / `dict[K, V]` and
  `Prodict` (plain dict to `Prodict`); Prodict subclasses (`from_dict`, unless the value
  already is an instance); `Optional[T]` / `T | None` / `Annotated[T, ...]` (as `T`).
  `List[T]` items go through `T` for any class `T` (`_convert_item`). Anything else (`Any`,
  `bool`, plain `tuple`, multi-type unions, unresolved strings) is stored as given, and so
  is a value whose conversion call raises: an annotation never makes an assignment
  fail. `None` is never converted.
  `p['key'] = ...` and `update()` are plain dict operations and bypass conversion.
- Unannotated plain dict values become `Prodict` instances; a Prodict is stored as it is.
- Names of `dict` methods (`DICT_RESERVED_KEYS`) are accepted as keys in data, but
  `set_attribute()` / `__setattr__` / `__delattr__` refuse them (`TypeError`).
- `__reduce__` returns the class (with `__getnewargs__` / `__getnewargs_ex__` if a
  subclass defines them), the instance attributes and slots (or a subclass's own
  `__getstate__()`), and the items, so `copy`, `deepcopy` and `pickle` (every protocol)
  restore the stored data without `init()` or conversion, and handle cycles. `__setstate__` restores attributes and slots
  and ignores the copy of the data that pickles from 0.8.x carry.
- Internal code calls `dict.items(self)` / `dict.keys(self)`, never `self.items()`, since a
  subclass may define a class attribute with that name.
- `__init__` and `set_attributes` name their first parameter
  `self_d921dfa9_4e93_4123_893d_a7e7eb783a32` so that `self` works as a key
  (`test_issue15`). Keep it that way.
- `to_dict()` options: `is_recursive`, `exclude_none`, `convert_list_items`,
  `exclude_none_in_lists` (legacy). See `docs/guides/serialization.md`.

Known limitations: dicts inside lists are not converted unless annotated (`List[Model]`),
and `p['key'] = ...` / `update()` store values without conversion.

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
