# Development

## Setup

The project uses [uv](https://docs.astral.sh/uv/). With uv installed, a checkout needs no
other setup: `uv run` creates the virtual environment and installs prodict plus the `dev`
dependency group on first use.

```bash
git clone https://github.com/ramazanpolat/prodict.git
cd prodict
uv run pytest
```

Without uv, use a virtual environment. On Python 3.9 and later, pip 25.1 or newer reads
the `dev` dependency group:

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e . --group dev
pytest
```

pip dropped Python 3.8 before it learned `--group`, so on 3.8 install pytest directly:
`pip install -e . 'pytest>=7'`.

## Layout

| Path | What |
|---|---|
| `prodict/__init__.py` | The whole library: the `Prodict` class and its helpers. |
| `test_prodict.py` | Unit tests. |
| `docs/` | Tutorial and guides. Their `>>>` blocks are doctests. |
| `examples/` | Runnable examples, each with a README showing its exact output. |
| `.github/workflows/pythonapp.yml` | CI: test matrix, build, deploy. |

## Tests

```bash
uv run pytest                                  # unit tests and doc tests
uv run pytest test_prodict.py -k to_dict       # a subset
uv run --python 3.8 pytest                     # another interpreter (uv downloads it)
for e in examples/*/main.py; do uv run python "$e"; done
```

`uv run pytest` runs `test_prodict.py` and every `>>>` example in `docs/` (configured in
`[tool.pytest.ini_options]`). When you change behavior, update the docs in the same change;
the doc tests fail otherwise. Example READMEs show each example's exact output, so update
them along with `main.py`.

CI runs the same commands on every Python version from 3.8 to 3.15.

## Lint

```bash
uvx flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

CI fails on these (syntax errors and undefined names) and reports the rest as warnings.

## Build

```bash
uv build                    # dist/prodict-<version>.tar.gz and .whl
uvx twine check dist/*
```

The wheel contains only the `prodict` package. The sdist adds the tests, docs, examples,
README, changelog and license, so the test suite runs from an unpacked sdist.
