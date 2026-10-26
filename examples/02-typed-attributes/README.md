# 02 - Typed attributes

Annotate a `Prodict` subclass and two things happen: your IDE can complete the attribute
names, and values are converted to the annotated type when they are set.

What it shows:

- `"83200000"` becomes the `int` `83200000` and `"357588"` the `float` `357588.0`;
- conversion also runs on later assignments;
- annotated attributes that were not given exist with the value `None`;
- `Any` turns conversion off while keeping completion;
- keys without an annotation are stored as they are.

See [the typed models guide](../../docs/guides/typed-models.md) for exactly which types are converted.

```bash
uv run python examples/02-typed-attributes/main.py
```

```
83200000 int
357588.0 float
{'name': 'Turkey', 'population': None, 'area_km2': None, 'raw': None}
02-typed-attributes: ok
```
