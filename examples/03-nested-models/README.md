# 03 - Nested models

When an attribute is annotated with a `Prodict` subclass, or with `List[...]` of one, plain
dicts in the input become instances of that class, all the way down.

What it shows:

- `cpu: Cpu` turns `{'cores': '16', ...}` into a `Cpu` with `cores == 16`;
- `rams: List[Ram]` turns each dict in the list into a `Ram`;
- methods defined on the model (`total_ram()`) work on the converted values;
- items appended to the list later are not converted, so build them as models.

```bash
uv run python examples/03-nested-models/main.py
```

```
Cpu 16
Ram 16
48
03-nested-models: ok
```
