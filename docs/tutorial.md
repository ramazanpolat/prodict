# Tutorial: from JSON to typed objects

This tutorial takes you from a plain dict to typed, nested models and back to JSON. It
takes about ten minutes. Every code block here is run by the test suite, so the output
you see is the output you get.

## 1. Install

```bash
pip install prodict
# or
uv add prodict
```

Prodict has no dependencies. It requires Python 3.8 or later and is tested on 3.8
through 3.15.

## 2. A dict with attributes

A `Prodict` is a `dict`. Keys are attributes and attributes are keys:

```python
>>> from prodict import Prodict
>>> p = Prodict(lang='Python')
>>> p.lang
'Python'
>>> p.version = 3
>>> p
{'lang': 'Python', 'version': 3}
>>> p['version'] == p.version
True
>>> isinstance(p, dict)
True

```

Nested dicts become Prodicts as well, so you can walk them with dots:

```python
>>> config = Prodict.from_dict({'db': {'host': 'localhost', 'port': 5432}})
>>> config.db.port
5432

```

## 3. Describe your data with a class

Plain dot access is convenient, but your IDE cannot know which attributes exist. Declare
them with annotations on a subclass:

```python
>>> class Country(Prodict):
...     name: str
...     population: int

>>> turkey = Country(name='Turkey', population='85000000')
>>> turkey.population
85000000

```

The IDE now completes `turkey.na...` to `turkey.name`, and `population` arrived as a
string but is stored as an `int`. Prodict converts values to the annotated type whenever
they are set. Attributes you did not pass exist with the value `None`:

```python
>>> Country(name='Nowhere')
{'name': 'Nowhere', 'population': None}

```

## 4. Nest models

Annotate an attribute with another Prodict subclass, or with `List[...]` of one, and
plain dicts in the input become instances of that class:

```python
>>> from typing import List

>>> class Comment(Prodict):
...     user_id: int
...     text: str

>>> class Post(Prodict):
...     title: str
...     comments: List[Comment]

>>> post = Post.from_dict({
...     'title': 'Hello',
...     'comments': [{'user_id': '2', 'text': 'Welcome!'}],
... })
>>> type(post.comments[0]).__name__
'Comment'
>>> post.comments[0].user_id
2

```

## 5. Give attributes defaults

Override `init()` (not `__init__`). Prodict calls it before applying the data you pass
in, keyword arguments or a positional dict, so the data wins, and you never call
`super()`:

```python
>>> class Settings(Prodict):
...     retries: int
...     timeout: float
...
...     def init(self):
...         self.retries = 3
...         self.timeout = 10.0

>>> Settings(retries='5')
{'retries': 5, 'timeout': 10.0}

```

## 6. Back to JSON

A Prodict is a dict, so `json.dumps` takes it as it is. `to_dict()` returns a plain
`dict` and can drop `None` values or convert nested models:

```python
>>> import json
>>> json.dumps(post)
'{"title": "Hello", "comments": [{"user_id": 2, "text": "Welcome!"}]}'
>>> Country(name='Nowhere').to_dict(exclude_none=True)
{'name': 'Nowhere'}

```

## Next steps

- [Typed models](guides/typed-models.md): which types are converted, and the rules for names.
- [Serialization](guides/serialization.md): every `to_dict()` option, copying and pickling.
- [Examples](../examples/): runnable programs, up to a complete JSON API client.
