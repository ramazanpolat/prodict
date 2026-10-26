# 01 - Basics

A `Prodict` is a `dict`. Every key is also an attribute, and every attribute you set is a key.

What it shows:

- keyword arguments and `Prodict.from_dict()` both build one;
- `p.key` and `p['key']` are the same value, and the object still compares equal to a plain dict;
- nested dicts become `Prodict` instances, so `config.db.host` works;
- a missing attribute raises `AttributeError`, so `getattr(p, 'name', default)` behaves as usual.

```bash
uv run python examples/01-basics/main.py
```

```
Python
Rocks!
{'lang': 'Python', 'pros': 'Rocks!', 'year': 1991}
localhost
'Prodict' object has no attribute 'cache'
01-basics: ok
```
