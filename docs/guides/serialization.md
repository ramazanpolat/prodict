# Serialization

A Prodict is already a `dict`, so anything that accepts a dict accepts a Prodict:
`json.dumps`, `dict(...)`, `**kwargs`, ORMs and HTTP clients. `to_dict()` is for when you
need a plain `dict` with a particular shape. Every code block is run by the test suite.

The examples below share these models:

```python
>>> import json
>>> from typing import List
>>> from prodict import Prodict

>>> class Tag(Prodict):
...     name: str
...     color: str

>>> class Note(Prodict):
...     title: str
...     author: Prodict
...     tags: List[Tag]
...     archived: bool

>>> note = Note.from_dict({
...     'title': 'Groceries',
...     'author': {'name': 'Ada', 'email': None},
...     'tags': [{'name': 'home', 'color': None}],
... })
>>> note
{'title': 'Groceries', 'author': {'name': 'Ada', 'email': None}, 'tags': [{'name': 'home', 'color': None}], 'archived': None}

```

## JSON

```python
>>> json.dumps(note)
'{"title": "Groceries", "author": {"name": "Ada", "email": null}, "tags": [{"name": "home", "color": null}], "archived": null}'

```

Going the other way is `Model.from_dict(json.loads(text))`.

## `to_dict()` options

`to_dict()` returns a new `dict`. All options are keyword-only and off by default.

| Option | Effect |
|---|---|
| `exclude_none=True` | Drop keys whose value is `None` (top level; nested levels too with `is_recursive`). |
| `is_recursive=True` | Convert nested Prodict values to plain dicts, recursively. |
| `convert_list_items=True` | Convert Prodict items inside lists to plain dicts. They follow `exclude_none`. |
| `exclude_none_in_lists=True` | Older form: convert list items and always drop their `None` values. |

### Default: one level

Only the top-level object becomes a `dict`. Nested values keep their types:

```python
>>> d = note.to_dict()
>>> type(d).__name__, type(d['author']).__name__, type(d['tags'][0]).__name__
('dict', 'Prodict', 'Tag')

```

### Drop `None` values

```python
>>> note.to_dict(exclude_none=True)
{'title': 'Groceries', 'author': {'name': 'Ada', 'email': None}, 'tags': [{'name': 'home', 'color': None}]}

```

`archived` is gone, but nested `None` values stay: `exclude_none` alone only looks at the
top level.

### Plain dicts all the way down

`is_recursive` converts nested Prodicts, and with `exclude_none` drops their `None`
values too. List items are a separate switch:

```python
>>> d = note.to_dict(is_recursive=True, exclude_none=True)
>>> d
{'title': 'Groceries', 'author': {'name': 'Ada'}, 'tags': [{'name': 'home', 'color': None}]}
>>> type(d['author']).__name__, type(d['tags'][0]).__name__
('dict', 'Tag')

```

Add `convert_list_items` for a structure with no Prodict left in it:

```python
>>> d = note.to_dict(is_recursive=True, exclude_none=True, convert_list_items=True)
>>> d
{'title': 'Groceries', 'author': {'name': 'Ada'}, 'tags': [{'name': 'home'}]}
>>> type(d['tags'][0]).__name__
'dict'

```

`convert_list_items` without `exclude_none` converts the items and keeps their `None`
values, which `exclude_none_in_lists` cannot do:

```python
>>> note.to_dict(convert_list_items=True)['tags']
[{'name': 'home', 'color': None}]
>>> note.to_dict(exclude_none_in_lists=True)['tags']
[{'name': 'home'}]

```

## Copying and pickling

`copy.deepcopy` keeps the model class and copies every nested value as it is stored:
`init()` does not run again and nothing is converted again. Shared and self-referencing
values are copied the way `deepcopy` copies them in a plain dict:

```python
>>> import copy
>>> clone = copy.deepcopy(note)
>>> type(clone).__name__, clone == note, clone is note, clone.author is note.author
('Note', True, False, False)

```

`pickle` round-trips a model the same way, as long as its class is importable (defined
at module level), the same rule as for any pickled class. See
[example 05](../../examples/05-json-api-client/main.py).

`copy.copy(note)` is shallow and keeps the class; `note.copy()` is shallow and returns a
plain `dict`, as it does for any dict subclass.
