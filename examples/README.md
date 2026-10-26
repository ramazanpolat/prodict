# Examples

Runnable examples, from the smallest to a complete round trip. Each folder has a
`main.py` that checks its own claims with `assert`, and CI runs every one of them on
every supported Python version, so the output shown here stays true.

| Example | Shows |
|---|---|
| [01-basics](01-basics/) | A Prodict is a dict with attribute access; nested dicts; missing attributes |
| [02-typed-attributes](02-typed-attributes/) | Annotations, automatic type conversion, `Any` |
| [03-nested-models](03-nested-models/) | Nested models and `List[Model]` built from plain data |
| [04-defaults](04-defaults/) | Default values with the `init()` hook |
| [05-json-api-client](05-json-api-client/) | JSON in, typed models, JSON out; `to_dict()`, `deepcopy`, `pickle` |

## Running them

From the repository root:

```bash
uv run python examples/01-basics/main.py
```

or, with prodict installed in any environment (`pip install prodict`):

```bash
python examples/01-basics/main.py
```

Every example ends by printing `<name>: ok`.
