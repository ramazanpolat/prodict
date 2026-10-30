# Prodict

[![PyPI](https://img.shields.io/pypi/v/prodict)](https://pypi.org/project/prodict/)
[![Python versions](https://img.shields.io/pypi/pyversions/prodict)](https://pypi.org/project/prodict/)
[![CI](https://github.com/ramazanpolat/prodict/actions/workflows/pythonapp.yml/badge.svg?branch=master)](https://github.com/ramazanpolat/prodict/actions/workflows/pythonapp.yml)
[![License: MIT](https://img.shields.io/github/license/ramazanpolat/prodict)](https://github.com/ramazanpolat/prodict/blob/master/LICENSE.txt)

**Prodict is a `dict` with dot-accessible attributes, IDE auto-completion, and type
conversion driven by annotations.**

```python
from typing import List
from prodict import Prodict

class Comment(Prodict):
    user_id: int
    text: str

class Post(Prodict):
    title: str
    comments: List[Comment]

post = Post.from_dict({'title': 'Hello', 'comments': [{'user_id': '2', 'text': 'Welcome!'}]})
post.comments[0].user_id   # 2, an int, and your IDE completes every name on the way
```

## Why

- `d['key1']['key2']['key3']` is noisy and easy to get wrong; `d.key1.key2.key3` is not.
- Web services talk JSON. Turning a JSON response into objects you can navigate, with
  the types you expect, should take one line.
- Declared attributes give you auto-completion in the IDE.
- It is still a `dict`: `json.dumps`, `==`, `**kwargs` and every dict method keep working.

## Installation

```bash
pip install prodict
# or
uv add prodict
```

No dependencies. Requires Python 3.8 or later; tested on 3.8 through 3.15.

## Features

**Dynamic attributes.** Keys are attributes and attributes are keys.

```python
p = Prodict(lang='Python', pros='Rocks!')
p.lang          # 'Python'
p.year = 1991
p               # {'lang': 'Python', 'pros': 'Rocks!', 'year': 1991}
isinstance(p, dict)  # True
```

**Nested dicts become Prodicts.**

```python
p = Prodict.from_dict({'package': 'Prodict', 'rock': {'even': 'more!'}})
p.rock.even     # 'more!'
type(p.rock)    # <class 'prodict.Prodict'>
```

**Type conversion from annotations.** Subclass `Prodict`, annotate attributes, and values
are converted when they are set. Use `Any` to keep completion without conversion.

```python
from typing import Any

class Country(Prodict):
    name: str
    population: int
    raw: Any

germany = Country(name='Germany', population='83200000', raw='83200000')
germany.population  # 83200000 (int)
germany.raw         # '83200000' (unchanged)
Country(name='Turkey')  # {'name': 'Turkey', 'population': None, 'raw': None}
```

![Auto-completion in PyCharm](https://raw.githubusercontent.com/ramazanpolat/prodict/master/docs/images/auto-complete1.png "Auto-completion in action")

**Nested models.** Attributes annotated with a Prodict subclass, or `List[...]` of one,
turn plain dicts into instances of that class.

```python
class Ram(Prodict):
    capacity: int
    unit: str

class Computer(Prodict):
    name: str
    rams: List[Ram]

    def total_ram(self):
        return sum(ram.capacity for ram in self.rams)

computer = Computer.from_dict({'name': 'Workstation', 'rams': [{'capacity': '16', 'unit': 'GB'}]})
isinstance(computer.rams[0], Ram)  # True
computer.total_ram()    # 16
```

**Defaults with `init()`.** Override `init()`, not `__init__`; no `super()` call needed,
and keyword arguments win over defaults.

```python
class Settings(Prodict):
    retries: int
    timeout: float

    def init(self):
        self.retries = 3
        self.timeout = 10.0

Settings(retries='5')   # {'retries': 5, 'timeout': 10.0}
```

**Serialization.** `to_dict()` returns a plain `dict` and can drop `None` values and
convert nested models and list items. `copy.deepcopy` and `pickle` keep model classes.

```python
Country(name='Turkey').to_dict(exclude_none=True)  # {'name': 'Turkey'}
```

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

user: User = User.from_dict(requests.get('https://example.com/api/users/1').json())
user.posts[0].comments[0].comment  # 'Good to see you blogging'
```

New keys can still be added to any of these objects at any time. A runnable version,
including writing the data back out, is [examples/05-json-api-client](https://github.com/ramazanpolat/prodict/tree/master/examples/05-json-api-client).

## Limitations

- Names of `dict` methods (`items`, `keys`, `get`, ...) cannot be attributes. Names of
  Prodict methods (`to_dict`, `from_dict`, `init`, ...) can be stored but are only readable
  with brackets, so avoid them.
- Keys that are not valid Python identifiers (`'1'`, `'first-name'`) work with brackets and
  `set_attribute()`, not with dots.
- Values are converted for `int`, `float`, `str`, `list`, `List[T]`, `Tuple[...]`,
  `Prodict` and its subclasses, when set as keyword arguments, through `from_dict()` or by
  attribute assignment. A `dict` or `Dict[K, V]` attribute turns a plain dict into a
  `Prodict` without converting its contents. `bool`, plain `tuple` and other types are
  stored as they come, and so is anything set with `p['key'] = ...` or `update()`.
- Prefer keyword arguments or `from_dict()`. A dict passed positionally (`Model({...})`)
  converts annotated attributes, but its unannotated nested dicts stay plain dicts.
- `Optional[...]`, `Union[...]`, and built-in generics such
  as `list[int]` are not supported as annotations; use `Any`, `Prodict` or the `typing`
  forms (`List[int]`).
- Prodict keeps data in the dict, not in instance attributes, so avoid giving class
  attributes values meant for instances.

The [typed models guide](https://github.com/ramazanpolat/prodict/blob/master/docs/guides/typed-models.md) covers each of these in detail.

## Documentation

- [Tutorial](https://github.com/ramazanpolat/prodict/blob/master/docs/tutorial.md): a ten-minute walk through every feature.
- [Typed models](https://github.com/ramazanpolat/prodict/blob/master/docs/guides/typed-models.md) and [Serialization](https://github.com/ramazanpolat/prodict/blob/master/docs/guides/serialization.md) guides.
- [Examples](https://github.com/ramazanpolat/prodict/tree/master/examples): runnable programs from the basics to a complete JSON API client.

Every Python example in `docs/` and `examples/` is run by CI on each supported Python version.

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
