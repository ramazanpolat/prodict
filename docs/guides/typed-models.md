# Typed models

Annotations on a `Prodict` subclass do two things: they let your IDE complete attribute
names, and they make Prodict convert values when they are set. This guide lists exactly
what is converted and what is not. Every code block is run by the test suite.

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

Conversion happens on construction, in `from_dict()`, and on every later assignment.

| Annotation | Conversion | Example input | Stored value |
|---|---|---|---|
| `int` | `int(value)` | `'42'` | `42` |
| `float` | `float(value)` | `'9.5'` | `9.5` |
| `str` | `str(value)` | `42` | `'42'` |
| `list` | `list(value)` | `('a', 'b')` | `['a', 'b']` |
| `List[T]` | each item through `T` | `['1', '2']` with `List[int]` | `[1, 2]` |
| a Prodict subclass | `Model.from_dict(value)` | `{'id': '1'}` | a `Model` instance |
| `List[Model]` | each item through `Model.from_dict` | `[{'id': '1'}]` | a list of `Model` |
| `dict` | `Prodict.from_dict(value)` | `{'a': 1}` | a `Prodict` |
| `Any` | none | anything | unchanged |

```python
>>> p = Product(name=7, price='9.5', stock='42', tags=('a', 'b'), extra='42')
>>> p
{'name': '7', 'price': 9.5, 'stock': 42, 'tags': ['a', 'b'], 'extra': '42'}
>>> p.stock = '41'
>>> p.stock
41

```

`None` is never converted: setting an annotated attribute to `None` stores `None`.

A value that cannot be converted raises the constructor's own error:

```python
>>> Product(stock='many')
Traceback (most recent call last):
    ...
ValueError: invalid literal for int() with base 10: 'many'

```

## What is not converted

- **`bool`, `tuple`, `set`** and other types not in the table are stored as they come.
  `bool` is deliberately left alone, since `bool('false')` would be `True`.
- **Items added to a list later** (`model.items_list.append({...})`) are not converted.
  Append model instances yourself.

```python
>>> class Flags(Prodict):
...     enabled: bool
...     size: tuple

>>> Flags(enabled='false', size=[1, 2])
{'enabled': 'false', 'size': [1, 2]}

```

## Unsupported annotations

- **`Optional[...]` and `Union[...]`**: values are stored unconverted on Python 3.13 and
  earlier, and setting a non-`None` value raises `AttributeError` on Python 3.14 and later.
  Annotate such attributes with `Any`.
- **`Dict[K, V]`**: setting a dict value raises `TypeError`. Annotate with `dict` or with
  a Prodict subclass instead.

## Unannotated keys

Keys without an annotation are allowed on any model and stored without conversion,
except that dicts become `Prodict` instances:

```python
>>> p = Product(name='pen', color='blue', size={'cm': 14})
>>> p.color, type(p.size).__name__
('blue', 'Prodict')

```

## Default values

Override `init()` to set defaults. It runs inside the constructor before the arguments
are applied, so arguments win:

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
  would shadow the method. Avoid them.
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
