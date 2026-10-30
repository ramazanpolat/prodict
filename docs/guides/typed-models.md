# Typed models

Annotations on a `Prodict` subclass do two things: they let your IDE complete attribute
names, and they make Prodict convert values when they are set. Conversion is a
convenience, not validation: a value Prodict cannot convert is stored as given, so an
annotation never makes an assignment fail. This guide lists exactly what is converted and
what is not. Every code block is run by the test suite.

## Declaring a model

```python
>>> from typing import Any, List
>>> from prodict import Prodict

>>> class Product(Prodict):
...     name: str
...     price: float
...     stock: int
...     tags: list
...     extra: Any

```

Every annotated attribute exists from the start, with the value `None` until you set it:

```python
>>> Product()
{'name': None, 'price': None, 'stock': None, 'tags': None, 'extra': None}

```

## What is converted

Conversion happens when a value goes through Prodict: keyword arguments to the
constructor, `from_dict()`, attribute assignment (`p.price = ...`) and `set_attribute()`.
Plain dict operations, `p['price'] = ...` and `p.update(...)`, store the value as it is.

| Annotation | Conversion | Example input | Stored value |
|---|---|---|---|
| `int` | `int(value)` | `'42'` | `42` |
| `float` | `float(value)` | `'9.5'` | `9.5` |
| `str` | `str(value)` | `42` | `'42'` |
| `list` | `list(value)` | `('a', 'b')` | `['a', 'b']` |
| `Tuple[...]` | `tuple(value)` | `[1, 2]` | `(1, 2)` |
| `List[T]` | each item through `T` | `['1', '2']` with `List[int]` | `[1, 2]` |
| a Prodict subclass | `Model.from_dict(value)` | `{'id': '1'}` | a `Model` instance |
| `List[Model]` | each item through `Model.from_dict` | `[{'id': '1'}]` | a list of `Model` |
| `Prodict`, `dict`, `Dict[K, V]` | `Prodict.from_dict(value)` | `{'a': 1}` | a `Prodict` |
| `Optional[T]` | through `T` | `'7'` with `Optional[int]` | `7` |
| `Any` | none | anything | unchanged |

The built-in generics `list[T]`, `tuple[...]` and `dict[K, V]` (Python 3.9+) work like
`List[T]`, `Tuple[...]` and `Dict[K, V]`, `T | None` (Python 3.10+) like
`Optional[T]`, and `Annotated[T, ...]` like `T`. A value that is already an instance of the annotated model is stored as it
is, not copied. `Dict[K, V]` does not convert keys and values to `K` and `V`; annotate
with a Prodict subclass for that.

```python
>>> p = Product(name=7, price='9.5', stock='42', tags=('a', 'b'), extra='42')
>>> p
{'name': '7', 'price': 9.5, 'stock': 42, 'tags': ['a', 'b'], 'extra': '42'}
>>> p.stock = '41'
>>> p.stock
41
>>> p['stock'] = '40'
>>> p.stock
'40'

```

`None` is never converted: setting an annotated attribute to `None` stores `None`.

A value that cannot be converted is stored as given, and so is an item of a `List[T]`:

```python
>>> Product(stock='many').stock
'many'
>>> class Order(Prodict):
...     quantities: List[int]

>>> Order(quantities=['1', 'two']).quantities
[1, 'two']

```

## What is not converted

- **`bool`, plain `tuple`, `set`** and other types not in the table are stored as they
  come. `bool` is deliberately left alone, since `bool('false')` would be `True`. Inside
  a `List[T]`, though, every item goes through `T` whatever class it is, so `List[bool]`,
  `List[tuple]` and `List[Decimal]` convert their items.
- **Unions of several types** (`Union[int, str]`) are stored as they come, since there is
  no single type to convert to.
- **Annotations that cannot be resolved**, such as a string naming a class that does not
  exist, are stored as they come; the model's other annotations still convert. String
  annotations that can be resolved, including those written with
  `from __future__ import annotations`, convert normally, and a forward reference starts
  converting once its class exists. On Python 3.9 and 3.10, a quoted name inside a
  built-in generic (`list['Node']`) is not resolved; write `List['Node']` there.
- **Items added to a list later** (`model.items_list.append({...})`) are not converted.
  Append model instances yourself.

```python
>>> from typing import Optional, Union

>>> class Flags(Prodict):
...     enabled: bool
...     size: tuple
...     code: Union[int, str]
...     retries: Optional[int]

>>> Flags(enabled='false', size=[1, 2], code='7', retries='3')
{'enabled': 'false', 'size': [1, 2], 'code': '7', 'retries': 3}

```

## Inheritance

A subclass of a model has the annotations of its base classes too:

```python
>>> class Base(Prodict):
...     id: int

>>> class User(Base):
...     name: str

>>> User()
{'id': None, 'name': None}
>>> User(id='1', name=2)
{'id': 1, 'name': '2'}

```

## Unannotated keys

Keys without an annotation are allowed on any model and stored without conversion,
except that dicts become `Prodict` instances:

```python
>>> p = Product(name='pen', color='blue', size={'cm': 14})
>>> p.color, type(p.size).__name__
('blue', 'Prodict')

```

## Passing data in

Give a model its data as keyword arguments, through `from_dict()`, or as a positional
dict. Annotated attributes are converted the same way in each case, and keyword arguments
win over a positional dict:

```python
>>> class Point(Prodict):
...     x: int

>>> Point(x='1'), Point.from_dict({'x': '1'}), Point({'x': '1'})
({'x': 1}, {'x': 1}, {'x': 1})
>>> Point({'x': '1'}, x='2')
{'x': 2}

```

## Default values

Override `init()` to set defaults. It runs inside the constructor before the keyword
arguments are applied, so keyword arguments win:

```python
>>> class Settings(Prodict):
...     retries: int
...     tags: List[str]
...
...     def init(self):
...         self.retries = 3
...         self.tags = []

>>> Settings(retries='5')
{'retries': 5, 'tags': []}

```

`init()` runs for every instance, so mutable defaults such as lists are never shared.

## Names you cannot use

- **Names of `dict` methods** (`items`, `keys`, `values`, `get`, `update`, `copy`, ...)
  cannot be attributes. Setting one raises `TypeError`.
- **Names of Prodict methods** (`to_dict`, `from_dict`, `init`, `set_attribute`, ...)
  can be set, but reading them with a dot still returns the method; only `p['to_dict']`
  reaches the value. Avoid them.
- **Keys that are not valid identifiers** (`'1'`, `'first-name'`) cannot be reached with a
  dot, but still work with brackets or `set_attribute()`:

```python
>>> p = Prodict()
>>> p.set_attribute('first-name', 'Ada')
>>> p['first-name']
'Ada'
>>> p.items = 1
Traceback (most recent call last):
    ...
TypeError: You cannot set a reserved name as attribute

```

## Class attributes

Prodict stores data in the dict, not in instance attributes. If a model has a class
attribute with a value, reading it on an instance returns the class value until you
assign to it, and an assignment then goes into the dict, where only `get()` and `[]`
can see it:

```python
>>> class Shop(Prodict):
...     currency: str = 'EUR'

>>> shop = Shop()
>>> shop.currency
'EUR'
>>> shop.currency = 'USD'
>>> shop.currency, shop['currency']
('EUR', 'USD')

```

Keep values meant for instances out of class attributes; use `init()` for defaults.
Annotate class-level settings with `ClassVar` to keep them out of the dict altogether:

```python
>>> from typing import ClassVar

>>> class Store(Prodict):
...     API_VERSION: ClassVar[int] = 2
...     currency: str

>>> Store(currency='EUR')
{'currency': 'EUR'}
>>> Store.API_VERSION
2

```
