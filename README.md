# Prodict

[![PyPI](https://img.shields.io/pypi/v/prodict)](https://pypi.org/project/prodict/)
[![Python versions](https://img.shields.io/pypi/pyversions/prodict)](https://pypi.org/project/prodict/)
[![CI](https://github.com/ramazanpolat/prodict/actions/workflows/pythonapp.yml/badge.svg?branch=master)](https://github.com/ramazanpolat/prodict/actions/workflows/pythonapp.yml)
[![License: MIT](https://img.shields.io/github/license/ramazanpolat/prodict)](https://github.com/ramazanpolat/prodict/blob/master/LICENSE.txt)

**Prodict is what Python's `dict` meant to be: a `dict` you can use with dots, typed by
your annotations and completed by your IDE.** It is still a real `dict`, and an
annotation never rejects a value.

```pycon
>>> from prodict import Prodict

>>> p = Prodict.from_dict({'package': 'Prodict', 'rocks': {'even': 'more!'}})
>>> p.package, p.rocks.even
('Prodict', 'more!')

```

## Installation

```bash
pip install prodict
# or
uv add prodict
```

No dependencies. Python 3.8 or later; tested on 3.8 through 3.15.

## Why Prodict

Declare the fields you care about, and values are converted on the way in:

```pycon
>>> from typing import List

>>> class Line(Prodict):
...     product: str
...     price: float
...     quantity: int

>>> class Order(Prodict):
...     id: int
...     lines: List[Line]
...
...     def total(self):
...         return sum(line.price * line.quantity for line in self.lines)

>>> order = Order.from_dict({
...     'id': '1001',
...     'lines': [{'product': 'pen', 'price': '1.50', 'quantity': '4'},
...               {'product': 'ink', 'price': 3.25, 'quantity': 2}],
... })
>>> order.id, order.lines[0].quantity, order.total()   # strings became numbers
(1001, 4, 12.5)
>>> order.lines[1]                                      # and it is still a dict
{'product': 'ink', 'price': 3.25, 'quantity': 2}

```

![Auto-completion in PyCharm](https://raw.githubusercontent.com/ramazanpolat/prodict/master/docs/images/auto-complete1.png "Your IDE completes the attributes you declare")

- `order.customer.address.city` reads better than `order['customer']['address']['city']`,
  and your IDE completes the fields you declared.
- JSON from an API or a config file becomes objects you can navigate, in one call.
- Annotations turn `'42'` into `42` and nested dicts into your own classes, methods
  included.
- It is a real `dict`: `json.dumps`, `==`, `**kwargs`, `isinstance(p, dict)` and every
  dict method keep working.
- It is lenient. A value it cannot convert is stored as it is and keys you did not declare
  are kept: an annotation never makes an assignment fail.
- It is small: one module, no dependencies.

| | `dict` | dataclass | pydantic model | **Prodict** |
|---|---|---|---|---|
| Is a `dict` (`json.dumps`, `**data`) | yes | no | no | **yes** |
| Dot access | no | yes | yes | **yes** |
| Nested data becomes your classes | no | no | yes | **yes** |
| `'42'` becomes `42` for an `int` field | no | no | yes | **yes** |
| Undeclared keys are kept | yes | no | if configured | **yes** |
| A value of the wrong type raises an error | no | no | yes | **no, it is kept** |
| Dependencies | none | none | a few | **none** |

If bad input should be rejected with an error, use a validation library such as
[pydantic](https://docs.pydantic.dev/). If you do not need a dict, a
[dataclass](https://docs.python.org/3/library/dataclasses.html) is simpler.

## Quick tour

### Keys are attributes

```pycon
>>> p = Prodict(lang='Python', pros='Rocks!')
>>> p.lang
'Python'
>>> p.year = 1991             # a new attribute is a new key
>>> p
{'lang': 'Python', 'pros': 'Rocks!', 'year': 1991}
>>> del p.year
>>> p == {'lang': 'Python', 'pros': 'Rocks!'}
True

```

A missing attribute raises `AttributeError`, so `getattr(p, 'name', default)` and
`hasattr()` behave as usual.

### Nested dicts become Prodicts

Through the constructor, `from_dict()` or dot assignment, dicts inside dicts become
Prodicts too. Dicts inside a list need an annotation such as `List[Model]` or
`List[dict]`.

```pycon
>>> config = Prodict({'db': {'host': 'localhost', 'port': 5432}})
>>> config.db.host
'localhost'
>>> config.cache = {'ttl': 60}
>>> config.cache.ttl
60

```

### Typed attributes

Subclass `Prodict` and annotate. Every annotated attribute exists from the start, `None`
until set, and values are converted on the way in.

```pycon
>>> from typing import Optional

>>> class Book(Prodict):
...     title: str
...     year: int
...     price: float
...     isbn: Optional[str]

>>> Book(title='Dune')
{'title': 'Dune', 'year': None, 'price': None, 'isbn': None}
>>> dune = Book(title='Dune', year='1965', price='9.99')
>>> dune.year + 1, dune.price
(1966, 9.99)
>>> Book(year='unknown').year       # cannot be converted: kept as given
'unknown'

```

What each annotation does with a value set through the constructor, `from_dict()` or an
attribute:

| Annotation | Example input | Stored value |
|---|---|---|
| `int`, `float`, `str` | `'42'` for `int` | `42` |
| `list` | `('a', 'b')` | `['a', 'b']` |
| `List[T]` | `['1', '2']` for `List[int]` | `[1, 2]`, each item through `T` |
| `Tuple[...]` | `['1', '2']` | `('1', '2')`, items unchanged |
| `Optional[T]` | `'7'` for `Optional[int]` | `7` |
| a Prodict subclass | `{'id': '1'}` | an instance of that class |
| `dict`, `Dict[K, V]`, `Prodict` | `{'a': '1'}` | a `Prodict`; keys and values are not converted to `K`, `V` |
| `Any`, `bool`, plain `tuple`, `Union[A, B]`, anything else | anything | unchanged |

On Python 3.9+, `list[int]`, `tuple[int, ...]`, `dict[str, int]` and
`Annotated[int, ...]` work too, and on 3.10+, `int | None`. String annotations and
`from __future__ import annotations` work as well (on 3.9 and 3.10, write
`List['Node']` rather than `list['Node']`). `None` is never converted. The
[typed models guide](https://github.com/ramazanpolat/prodict/blob/master/docs/guides/typed-models.md)
has the details.

### Defaults and inheritance

Override `init()`, not `__init__`, to set defaults; the data you pass in wins over them.
A subclass has its base classes' attributes and defaults; if it overrides `init()` too,
it calls `super().init()` to keep them.

```pycon
>>> class Settings(Prodict):
...     retries: int
...     timeout: float
...
...     def init(self):
...         self.retries = 3
...         self.timeout = 10.0

>>> class ServerSettings(Settings):
...     host: str

>>> ServerSettings(host='example.com', retries='5')
{'host': 'example.com', 'retries': 5, 'timeout': 10.0}

```

### JSON, copies and any key

```pycon
>>> import json
>>> json.dumps(dune)
'{"title": "Dune", "year": 1965, "price": 9.99, "isbn": null}'
>>> dune.to_dict(exclude_none=True)
{'title': 'Dune', 'year': 1965, 'price': 9.99}
>>> page = Prodict.from_dict({'items': [1, 2], 'total': 2})
>>> page['items'], page.total      # names of dict methods are fine as keys
([1, 2], 2)

```

`to_dict()` works on the top level; `is_recursive=True` converts nested models too (see
the [serialization guide](https://github.com/ramazanpolat/prodict/blob/master/docs/guides/serialization.md)).
`copy.copy`, `copy.deepcopy` and `pickle` keep the model class and the data as it is,
while `p.copy()` returns a plain `dict`, as for any dict subclass. `dir(p)` lists the
keys that are identifiers, so a REPL or notebook completes them too.

## A real API in a few lines

Declare only the fields you use; everything else in the response is kept and reachable
too. With [Requests](https://requests.readthedocs.io/) installed
(`pip install requests`), this runs against the GitHub API:

```python
import json
from typing import List, Optional

import requests
from prodict import Prodict

class Owner(Prodict):
    login: str

class License(Prodict):
    spdx_id: str

class Repo(Prodict):
    full_name: str
    stargazers_count: int
    owner: Owner
    license: Optional[License]
    topics: List[str]

repo = Repo.from_dict(requests.get('https://api.github.com/repos/ramazanpolat/prodict').json())
repo.owner.login        # 'ramazanpolat', and your IDE completed it
repo.license.spdx_id    # 'MIT' (license is None for a repository without one)
repo.description        # not declared, still there
repo.owner.html_url     # undeclared nested fields too
json.dumps(repo)        # back to JSON, every field included
```

Without Prodict, the same reads are `data['owner']['login']` and
`data['license']['spdx_id']`, with no completion and no types. A runnable program that
reads JSON into typed models, computes with them and writes JSON back is
[examples/05-json-api-client](https://github.com/ramazanpolat/prodict/tree/master/examples/05-json-api-client).

## Good to know

- Names of `dict` methods (`items`, `keys`, `get`, ...) and of Prodict methods
  (`to_dict`, `from_dict`, `init`, ...) work as keys, but reading them with a dot returns
  the method: use `p['items']`. Setting or deleting a `dict` method name with a dot
  raises `TypeError`. Names like `__deepcopy__` are bracket-only too.
- Keys that are not valid identifiers (`'first-name'`, `1`) or are Python keywords
  (`'class'`, `'from'`) cannot be used with a dot; use brackets, or `set_attribute()` to
  store a value with conversion.
- `p['key'] = ...`, `update()` and later changes such as `p.tags.append('4')` store
  values as they are, without conversion.
- Data lives in the dict, not in instance attributes: set defaults in `init()`, not as
  class attributes, and annotate class-level settings with `ClassVar`.

## Upgrading from 0.8

0.9 makes Prodict lenient and more dict-like. What you may notice:

- A value that cannot be converted is stored as given instead of raising `ValueError` or
  `TypeError`.
- `Optional[T]`, `T | None`, built-in generics (`list[int]`) and string annotations
  work, and a subclass inherits its base classes' annotations.
- `Model({...})` works like `Model.from_dict({...})`, nested dicts included, and keys
  such as `items` work in data.
- A Prodict you pass in is stored as it is, not copied, when the field is unannotated or
  it already has the annotated class; `deepcopy` and `pickle` no longer run `init()` or
  convert values again.

The [changelog](https://github.com/ramazanpolat/prodict/blob/master/CHANGELOG.md) lists
every change.

## Documentation

- [Tutorial](https://github.com/ramazanpolat/prodict/blob/master/docs/tutorial.md): a ten-minute walk through every feature.
- [Typed models](https://github.com/ramazanpolat/prodict/blob/master/docs/guides/typed-models.md) and [Serialization](https://github.com/ramazanpolat/prodict/blob/master/docs/guides/serialization.md) guides.
- [Examples](https://github.com/ramazanpolat/prodict/tree/master/examples): runnable programs from the basics to a complete JSON API client.

The `>>>` examples in this README and in `docs/`, and every program in `examples/`, run in
CI on each supported Python version.

## Contributing

Bug reports and pull requests are welcome. See [CONTRIBUTING.md](https://github.com/ramazanpolat/prodict/blob/master/CONTRIBUTING.md) for
setup and tests, and [CHANGELOG.md](https://github.com/ramazanpolat/prodict/blob/master/CHANGELOG.md) for what changed between releases.

## License

MIT. See [LICENSE.txt](https://github.com/ramazanpolat/prodict/blob/master/LICENSE.txt).

## Thanks

To [JetBrains](https://www.jetbrains.com/) for [PyCharm](https://www.jetbrains.com/pycharm/),
the IDE that made my life better.

<a href="https://www.jetbrains.com/"><img src="https://raw.githubusercontent.com/ramazanpolat/prodict/master/docs/images/jetbrains.png" alt="JetBrains" height="64"></a>
<a href="https://www.jetbrains.com/pycharm/"><img src="https://raw.githubusercontent.com/ramazanpolat/prodict/master/docs/images/pycharm.png" alt="PyCharm" height="64"></a>
