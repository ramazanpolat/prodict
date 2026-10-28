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
| `Prodict` | `Prodict.from_dict(value)` | `{'a': 1}` | a `Prodict` |
| `Any` | none | anything | unchanged |

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

A value that cannot be converted raises the constructor's own error:

```python
>>> Product(stock='many')
Traceback (most recent call last):
    ...
ValueError: invalid literal for int() with base 10: 'many'

```

## What is not converted

- **`bool`, plain `tuple`, `set`** and other types not in the table are stored as they
  come. `bool` is deliberately left alone, since `bool('false')` would be `True`. (A
  Prodict value given to such an attribute raises `AttributeError`.)
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

- **`Optional[...]` and `Union[...]`**: depending on the value and the Python version, a
  value is stored unconverted or raises an error (a dict raises `TypeError` and a Prodict
  raises `AttributeError` everywhere; on Python 3.14 and later other non-`None` values raise
  `AttributeError` too). Annotate such attributes with `Any`.
- **`Dict[K, V]`**: setting a dict value raises `TypeError`. Annotate with `Prodict` or
  a Prodict subclass instead.
- **`dict`**: a plain dict is converted to a `Prodict`, but assigning a Prodict value
  raises `AttributeError`, and so does `copy.deepcopy()` of the model while the attribute
  holds a Prodict (which every plain dict assigned to it becomes). Annotate with `Prodict` instead.
- **Built-in generics** (`list[int]`, `tuple[int, ...]`, `dict[str, int]`): raise an error
  (`KeyError` or `TypeError`) for most values. Use the `typing` forms (`List[int]`, `Tuple[int, ...]`).

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
