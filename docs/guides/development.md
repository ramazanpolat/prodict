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

pip dropped Python 3.8 before it learned `--group`, so on 3.8 install the tools directly:
`pip install -e . 'pytest>=7' 'coverage[toml]>=7'`.

## Layout

| Path | What |
|---|---|
| `prodict/__init__.py` | The whole library: the `Prodict` class and its helpers. |
| `test_prodict.py` | Unit tests. |
| `docs/` | Tutorial and guides. Their `>>>` blocks are doctests. |
| `examples/` | Runnable examples, each with a README showing its exact output. |
| `.github/workflows/pythonapp.yml` | CI: test matrix, combined coverage, build, deploy. |

## Tests

```bash
uv run pytest                                  # unit tests and doc tests
uv run pytest test_prodict.py -k to_dict       # a subset
uv run --python 3.8 pytest                     # another interpreter (uv downloads it)
for e in examples/*/main.py; do uv run python "$e"; done
```

`uv run pytest` runs `test_prodict.py` and every `>>>` example in `docs/` and `README.md`
(configured in `[tool.pytest.ini_options]`). When you change behavior, update the docs in
the same change; the doc tests fail otherwise. Example READMEs show each example's exact output, so update
them along with `main.py`.

CI runs the same commands on every Python version from 3.8 to 3.15.

## Coverage

Every line and branch of `prodict/__init__.py` is covered by the tests. Some lines run only
on some Python versions (3.8 and 3.9 fallbacks, `annotationlib` on 3.14+), so coverage is
measured on each version and combined; CI fails below 100% (`fail_under` in
`[tool.coverage.report]`).

```bash
for v in 3.8 3.9 3.10 3.11 3.12 3.13 3.14 3.15; do
  COVERAGE_FILE=.coverage.$v uv run --python $v coverage run -m pytest -q
done
uv run coverage combine && uv run coverage report
```

On one interpreter, `uv run coverage run -m pytest && uv run coverage report` lists the
lines that interpreter leaves out; the lines for other versions show up there as missing.

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
