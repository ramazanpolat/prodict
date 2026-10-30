# Prodict

[![PyPI](https://img.shields.io/pypi/v/prodict)](https://pypi.org/project/prodict/)
[![Python versions](https://img.shields.io/pypi/pyversions/prodict)](https://pypi.org/project/prodict/)
[![CI](https://github.com/ramazanpolat/prodict/actions/workflows/pythonapp.yml/badge.svg?branch=master)](https://github.com/ramazanpolat/prodict/actions/workflows/pythonapp.yml)
[![License: MIT](https://img.shields.io/github/license/ramazanpolat/prodict)](https://github.com/ramazanpolat/prodict/blob/master/LICENSE.txt)

**A Python `dict` you can also use with dots.** Annotate a subclass, and Prodict converts
the values and your IDE completes the names. It stays a real `dict` that never refuses
data.

```python
>>> from typing import List
>>> from prodict import Prodict

>>> class Comment(Prodict):
...     user_id: int
...     text: str

>>> class Post(Prodict):
...     title: str
...     comments: List[Comment]

>>> post = Post.from_dict({'title': 'Hello', 'comments': [{'user_id': '2', 'text': 'Welcome!'}]})
>>> post.comments[0].user_id   # an int now, and your IDE completed every name on the way
2
>>> post                       # still a dict
{'title': 'Hello', 'comments': [{'user_id': 2, 'text': 'Welcome!'}]}

```

## Why Prodict

- `data.user.address.city` reads better than `data['user']['address']['city']`, and is
  harder to get wrong.
- JSON from a web service becomes objects you can navigate, with the types you declared,
  in one call.
- Declared attributes give you auto-completion and type hints in your IDE.
- It is a real `dict`: `json.dumps`, `==`, `**kwargs`, `isinstance(p, dict)` and every
  dict method keep working.
- It is lenient. Annotations convert what they can, a value they cannot convert is stored
  as it is, and keys you did not declare are welcome. Unexpected data never raises.

Prodict does not validate. If bad input should be rejected with an error, use a
validation library such as [pydantic](https://docs.pydantic.dev/). If you do not need a
dict, a [dataclass](https://docs.python.org/3/library/dataclasses.html) is simpler.

## Installation

```bash
pip install prodict
# or
uv add prodict
```

No dependencies. Requires Python 3.8 or later; tested on 3.8 through 3.15. Upgrading from
0.8? Conversion became lenient in 0.9; the
[changelog](https://github.com/ramazanpolat/prodict/blob/master/CHANGELOG.md) lists what
changed.

## Quick tour

### Dot access

Keys are attributes and attributes are keys.

```python
>>> p = Prodict(lang='Python', pros='Rocks!')
>>> p.lang
'Python'
>>> p.year = 1991
>>> del p.pros
>>> p
{'lang': 'Python', 'year': 1991}
>>> isinstance(p, dict)
True

```

### Nested dicts become Prodicts

At every level, however the data comes in: `from_dict()`, a positional dict, or keyword
arguments.

```python
>>> p = Prodict.from_dict({'package': 'Prodict', 'rock': {'even': 'more!'}})
>>> p.rock.even
'more!'
>>> Prodict({'rock': {'even': 'more!'}}).rock.even
'more!'

```

### Typed attributes

Subclass `Prodict` and annotate. Every annotated attribute exists from the start, as
`None` until set, and values are converted when they come in.

```python
>>> from typing import Any, Optional

>>> class Country(Prodict):
...     name: str
...     population: int
...     capital: Optional[str]
...     raw: Any

>>> Country(name='Turkey')
{'name': 'Turkey', 'population': None, 'capital': None, 'raw': None}
>>> germany = Country(name='Germany', population='83200000', raw='83200000')
>>> germany.population, germany.raw
(83200000, '83200000')
>>> Country(population='unknown').population   # cannot be converted: stored as given
'unknown'

```

![Auto-completion in PyCharm](https://raw.githubusercontent.com/ramazanpolat/prodict/master/docs/images/auto-complete1.png "Auto-completion in action")

What each annotation does with a value set through the constructor, `from_dict()` or an
attribute:

| Annotation | Example input | Stored value |
|---|---|---|
| `int`, `float`, `str` | `'42'` for `int` | `42` |
| `list`, `Tuple[...]` | `('a', 'b')` for `list` | `['a', 'b']` |
| `List[T]` | `['1', '2']` for `List[int]` | `[1, 2]` |
| `Optional[T]` | `'7'` for `Optional[int]` | `7` |
| a Prodict subclass | `{'id': '1'}` | an instance of that class |
| `dict`, `Dict[K, V]`, `Prodict` | `{'a': 1}` | a `Prodict` |
| `Any`, `bool`, `Union[A, B]`, anything else | anything | unchanged |

The built-in forms work too (`list[int]`, `dict[str, int]`, `int | None`), and so do
string annotations and `from __future__ import annotations`. `None` is never converted,
and `p['key'] = ...` and `update()` store values unchanged, as in any dict. The
[typed models guide](https://github.com/ramazanpolat/prodict/blob/master/docs/guides/typed-models.md)
has the details.

### Nested models

Attributes annotated with a Prodict subclass, or `List[...]` of one, turn plain dicts into
instances of that class, methods included.

```python
>>> class Ram(Prodict):
...     capacity: int
...     unit: str

>>> class Computer(Prodict):
...     name: str
...     rams: List[Ram]
...
...     def total_ram(self):
...         return sum(ram.capacity for ram in self.rams)

>>> computer = Computer.from_dict({'name': 'Workstation', 'rams': [{'capacity': '16', 'unit': 'GB'}]})
>>> type(computer.rams[0]).__name__, computer.total_ram()
('Ram', 16)

```

### Inheritance and defaults

A subclass has its base classes' attributes. Override `init()`, not `__init__`, to set
defaults: no `super()` call is needed, and the data you pass in wins over them.

```python
>>> class Settings(Prodict):
...     retries: int
...     timeout: float
...
...     def init(self):
...         self.retries = 3
...         self.timeout = 10.0

>>> class ServerSettings(Settings):
...     host: str

>>> ServerSettings(retries='5', host='example.com')
{'retries': 5, 'host': 'example.com', 'timeout': 10.0}

```

### JSON, copies and any key

```python
>>> import json
>>> json.dumps(Country(name='Turkey'))
'{"name": "Turkey", "population": null, "capital": null, "raw": null}'
>>> Country(name='Turkey').to_dict(exclude_none=True)
{'name': 'Turkey'}
>>> page = Prodict.from_dict({'items': [1, 2], 'total': 2})
>>> page['items'], page.total   # names of dict methods are fine as keys
([1, 2], 2)

```

`copy.copy`, `copy.deepcopy` and `pickle` keep the model class and the data as it is.
`dir(p)` lists the keys, so a REPL or notebook completes them too.

## A complete example

Suppose `https://example.com/api/users/1` returns:

```json
{
  "user_id": 1,
  "user_name": "rambo",
  "posts": [
    {
      "title": "Hello World",
      "date": "2018-01-02 03:04:05",
      "comments": [
        {"user_id": 2, "comment": "Good to see you blogging", "date": "2018-01-02 03:04:06"}
      ]
    }
  ]
}
```

Without Prodict, you write the classes and the mapping by hand:

```python
class Comment:
    def __init__(self, user_id, comment, date):
        self.user_id = user_id
        self.comment = comment
        self.date = date

class Post:
    def __init__(self, title, date, comments):
        self.title = title
        self.date = date
        self.comments = comments

class User:
    def __init__(self, user_id, user_name, posts):
        self.user_id = user_id
        self.user_name = user_name
        self.posts = posts

data = requests.get('https://example.com/api/users/1').json()
user = User(
    data['user_id'],
    data['user_name'],
    [
        Post(p['title'], p['date'], [Comment(c['user_id'], c['comment'], c['date']) for c in p['comments']])
        for p in data['posts']
    ],
)
```

With Prodict, you declare the shape and let it do the rest:

```python
class Comment(Prodict):
    user_id: int
    comment: str
    date: str

class Post(Prodict):
    title: str
    date: str
    comments: List[Comment]

class User(Prodict):
    user_id: int
    user_name: str
    posts: List[Post]

user = User.from_dict(requests.get('https://example.com/api/users/1').json())
user.posts[0].comments[0].comment   # 'Good to see you blogging'
json.dumps(user)                    # back to JSON
```

Fields the API adds later are kept too, and reachable by dot. A runnable version is
[examples/05-json-api-client](https://github.com/ramazanpolat/prodict/tree/master/examples/05-json-api-client).

## Good to know

- Names of `dict` methods (`items`, `keys`, `get`, ...) and of Prodict methods
  (`to_dict`, `from_dict`, `init`, ...) work as keys, but reading them with a dot returns
  the method: use `p['items']`. Names like `__deepcopy__` are bracket-only too.
- Keys that are not valid identifiers (`'first-name'`, `1`) cannot be read with a dot; use
  brackets, or `set_attribute()` to store a value with conversion.
- `p['key'] = ...` and `update()` store values as they are, without conversion.
- Dicts inside a list stay dicts unless the list is annotated (`List[Model]`).
- Data lives in the dict, not in instance attributes: set defaults in `init()`, not as
  class attributes, and annotate class-level settings with `ClassVar`.

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
