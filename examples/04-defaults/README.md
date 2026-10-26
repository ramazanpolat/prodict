# 04 - Default values

Override `init()` (not `__init__`) to set defaults. Prodict calls it from its own
constructor before applying the keyword arguments you passed, so you never call `super()`
and keyword arguments always win over defaults.

What it shows:

- `Settings()` gets every default;
- `Settings(retries='5')` replaces one default and converts it to `int`;
- a mutable default such as a list is created fresh for every instance.

```bash
uv run python examples/04-defaults/main.py
```

```
{'retries': 3, 'timeout': 10.0, 'tags': []}
{'retries': 5, 'verbose': True, 'timeout': 10.0, 'tags': []}
04-defaults: ok
```
