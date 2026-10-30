# Global comments:
# self is avoided to fix #15
from typing import Any, ClassVar, ForwardRef, List, Union, get_args, get_origin, get_type_hints
import re
import sys
import threading
import typing

DICT_RESERVED_KEYS = vars(dict).keys()


class GenericMeta(type):
    pass


def _dict_value(v, is_recursive, exclude_none, exclude_none_in_lists, convert_list_items):
    if is_recursive and isinstance(v, Prodict):
        return v.to_dict(is_recursive=is_recursive, exclude_none=exclude_none,
                        exclude_none_in_lists=exclude_none_in_lists,
                        convert_list_items=convert_list_items)

    # Handle lists: convert items to dict if requested
    if isinstance(v, List) and (convert_list_items or exclude_none_in_lists):
        # Determine whether to exclude None from list items
        # If exclude_none_in_lists=True, always exclude None (legacy behavior)
        # Otherwise, respect the parent's exclude_none setting
        list_item_exclude_none = True if exclude_none_in_lists else exclude_none

        return [
            item.to_dict(exclude_none=list_item_exclude_none,
                        is_recursive=is_recursive,
                        exclude_none_in_lists=exclude_none_in_lists,
                        convert_list_items=convert_list_items)
            if isinstance(item, Prodict)
            else item
            for item in v
        ]

    return v


try:
    from types import UnionType as _UnionType  # X | Y, Python 3.10+
    _UNION_TYPES = (Union, _UnionType)
except ImportError:
    _UNION_TYPES = (Union,)

_ANNOTATED = getattr(typing, 'Annotated', None)  # Python 3.9+

try:
    import annotationlib  # Python 3.14+, where annotations are evaluated lazily
except ImportError:
    annotationlib = None

# the class attribute that holds a model's annotations, collected over its
# class hierarchy: (annotations, {name: (owner class, annotation)} not resolved yet).
# Not an identifier, so it can never hide a key from attribute access.
_ATTR_TYPES = 'prodict:attr_types'
_attr_types_lock = threading.RLock()

# ClassVar, bare or subscripted, written as a string, with what precedes it
# (typing., an alias such as t., or nothing)
_CLASS_VAR = re.compile(r'((?:\w+\.)*)ClassVar\s*(?:\[|$)')


def _own_annotations(klass):
    # the annotations a class declares itself, unevaluated where they cannot be
    if annotationlib is not None:
        return annotationlib.get_annotations(klass, format=annotationlib.Format.FORWARDREF)
    return klass.__dict__.get('__annotations__', {})


def _resolve(owner, annotation):
    # resolves one annotation of class owner, looking names up in the same
    # namespaces, in the same order, as typing.get_type_hints() does for a class
    module_ns = getattr(sys.modules.get(owner.__module__), '__dict__', {})
    if sys.version_info >= (3, 10):
        globalns, localns = dict(vars(owner)), module_ns
    else:
        globalns, localns = module_ns, None
    holder = type('_Annotation', (), {'__annotations__': {'a': annotation}})
    return get_type_hints(holder, globalns=globalns, localns=localns)['a']


def _lookup(owner, dotted_name):
    # the object a dotted name refers to in the class body of owner, or None
    module_ns = getattr(sys.modules.get(owner.__module__), '__dict__', {})
    first, *rest = dotted_name.split('.')
    try:
        obj = module_ns.get(first, vars(owner).get(first))
        for name in rest:
            obj = getattr(obj, name, None)
    except Exception:
        # a lazy module or proxy that fails on attribute access
        return None
    return obj


def _is_class_var(tp, owner=None):
    if _ANNOTATED is not None and get_origin(tp) is _ANNOTATED:
        tp = get_args(tp)[0]
    if isinstance(tp, ForwardRef):
        tp = tp.__forward_arg__
    if isinstance(tp, str):
        match = _CLASS_VAR.match(tp.strip())
        if match is None:
            return False
        prefix = match.group(1)
        if prefix in ('', 'typing.'):
            return True
        # t.ClassVar after `import typing as t` is ClassVar; models.ClassVar,
        # a class named ClassVar, is not
        return owner is not None and _lookup(owner, prefix + 'ClassVar') is ClassVar
    return tp is ClassVar or get_origin(tp) is ClassVar


def _collect_annotations(cls):
    """
    Returns the annotations of cls and its base classes, resolved where
    possible, and the ones that could not be resolved yet.
    """
    try:
        resolved = get_type_hints(cls)
    except Exception:
        resolved = None
    types, unresolved = {}, {}
    for klass in reversed(cls.__mro__):
        for name, annotation in _own_annotations(klass).items():
            unresolved.pop(name, None)  # a subclass may redeclare it
            if resolved is not None:
                annotation = resolved[name]
            else:
                # resolve one by one, so that one annotation that cannot be
                # resolved does not stop the others from converting
                try:
                    annotation = _resolve(klass, annotation)
                except Exception:
                    unresolved[name] = (klass, annotation)
            types[name] = annotation
    return _without_class_vars(types, unresolved)


def _retry_unresolved(types, unresolved):
    # a forward reference may name a class that exists by now
    types, unresolved = dict(types), dict(unresolved)
    for name, (owner, annotation) in list(unresolved.items()):
        try:
            types[name] = _resolve(owner, annotation)
        except Exception:
            continue
        del unresolved[name]
    return _without_class_vars(types, unresolved)


def _without_class_vars(types, unresolved):
    # ClassVar annotations are class attributes, not keys
    for name, annotation in list(types.items()):
        owner = unresolved[name][0] if name in unresolved else None
        if _is_class_var(annotation, owner):
            del types[name]
            unresolved.pop(name, None)
    return types, unresolved


def _try(constructor, value):
    try:
        return constructor(value)
    except Exception:
        # the value cannot be converted: store it as given
        return value


def _convert(tp, value):
    """
    Converts value to the annotation tp where Prodict knows how, and returns
    it unchanged otherwise. An annotation never makes an assignment fail.
    """
    if value is None or tp is Any:
        return value
    origin = get_origin(tp)
    if origin in _UNION_TYPES:
        # Optional[X], Union[X, None] and X | None convert as X; any other
        # union stores the value as given
        args = [a for a in get_args(tp) if a is not type(None)]
        return _convert(args[0], value) if len(args) == 1 else value
    if _ANNOTATED is not None and origin is _ANNOTATED:
        return _convert(get_args(tp)[0], value)
    if tp in (int, float, str, list):
        return _try(tp, value)
    if tp is dict or origin is dict:
        # dict, Dict and Dict[K, V]: a plain dict becomes a Prodict; keys and
        # values are not converted
        if isinstance(value, dict) and not isinstance(value, Prodict):
            # a key Prodict cannot hold as an attribute, such as 'items',
            # keeps the dict as given
            return _try(Prodict.from_dict, value)
        return value
    if isinstance(tp, type) and origin is None and issubclass(tp, Prodict):
        if isinstance(value, dict) and not isinstance(value, tp):
            return tp.from_dict(value)
        return value
    if origin is list:
        # List, List[T] and list[T]; a mapping is stored as given
        if isinstance(value, dict):
            return value
        items = _try(list, value)
        if items is value:
            return value
        args = get_args(tp)
        if args:
            return [_convert_item(args[0], item) for item in items]
        return items
    if origin is tuple:
        # Tuple, Tuple[...] and tuple[...]; items are not converted
        if isinstance(value, dict):
            return value
        return _try(tuple, value)
    # bool, plain tuple, other classes, string annotations that could not be
    # resolved, and anything else: stored as given
    return value


def _convert_item(tp, item):
    # List[T] passes each item through T, also for classes that are stored as
    # given at the top level, such as bool, tuple or Decimal
    if item is None:
        return item
    origin = get_origin(tp)
    if origin in _UNION_TYPES:
        args = [a for a in get_args(tp) if a is not type(None)]
        return _convert_item(args[0], item) if len(args) == 1 else item
    if _ANNOTATED is not None and origin is _ANNOTATED:
        return _convert_item(get_args(tp)[0], item)
    if (tp is not Any and isinstance(tp, type) and origin is None
            and tp not in (int, float, str, list, dict) and not issubclass(tp, Prodict)):
        try:
            if isinstance(item, tp):
                return item
        except Exception:
            # a class that does not support isinstance(), such as a TypedDict
            return item
        return _try(tp, item)
    return _convert(tp, item)


def _store(prodict, key, value):
    """
    Stores value under key, converted as the key's annotation says; an
    unannotated plain dict becomes a Prodict. Any key a dict accepts is
    accepted, including names of dict methods and keys that are not strings.
    """
    types = prodict.attr_types()  # one snapshot for the lookup and the conversion
    if key in types:
        value = _convert(types[key], value)
    elif isinstance(value, dict) and not isinstance(value, Prodict):
        value = Prodict.from_dict(value)
    dict.__setitem__(prodict, key, value)


def _none_condition(v, is_recursive, exclude_none):
    return v is not None if exclude_none else True


# noinspection PyMethodParameters
class Prodict(dict):
    """
    Prodict = Dictionary with IDE friendly(auto code completion),
    dot-accessible attributes and more.
    """

    def __init__(self_d921dfa9_4e93_4123_893d_a7e7eb783a32, *args, **kwargs):
        self = self_d921dfa9_4e93_4123_893d_a7e7eb783a32
        super().__init__(*args, **kwargs)

        # #55, #42: the data that arrived positionally (a dict or an iterable of
        # pairs, possibly a one-shot iterator), read back from the dict itself
        positional = {k: v for k, v in self.items() if k not in kwargs}

        # #3: every annotated attribute exists, None until set
        for k in self.attr_types():
            dict.__setitem__(self, k, None)

        # defaults first, then the data: positional values, then keyword arguments
        self.init()
        for k, v in positional.items():
            _store(self, k, v)
        for k, v in kwargs.items():
            _store(self, k, v)

    def init(self):
        ...

    def __new__(cls, *args, **kwargs):
        return super(Prodict, cls).__new__(cls, *args, **kwargs)

    def __setstate__(self, state):
        # pickle and copy restore the data as it is stored, without init() or
        # conversion; pickles from 0.8.x carry a copy of the data as state,
        # which is not needed
        pass

    @classmethod
    def from_dict(cls, d: dict):
        return cls(d)

    @classmethod
    def attr_has_default_value(cls, attr_name: str) -> bool:
        return bool(hasattr(cls, attr_name))

    @classmethod
    def get_attr_default_value(cls, attr_name: str):
        if cls.attr_has_default_value(attr_name):
            return getattr(cls, attr_name)
        else:
            return None

    @classmethod
    def attr_type(cls, attr_name: str):
        return cls.attr_types()[attr_name]

    @classmethod
    def attr_types(cls):
        """
        Returns the annotations of the class and its base classes. String
        annotations are resolved where possible; ClassVar annotations are left
        out.
        """
        entry = cls.__dict__.get(_ATTR_TYPES)
        if entry is None or entry[1]:
            with _attr_types_lock:
                entry = cls.__dict__.get(_ATTR_TYPES)
                if entry is None:
                    entry = _collect_annotations(cls)
                elif entry[1]:
                    entry = _retry_unresolved(*entry)
                setattr(cls, _ATTR_TYPES, entry)
        return entry[0]

    @classmethod
    def attr_names(cls) -> List[str]:
        """
        Returns annotated attribute names
        :return: List[str]
        """
        return [k for k, v in cls.attr_types().items()]

    @classmethod
    def has_attr(cls, attr_name: str):
        """
        Returns True if class have an annotated attribute
        :param attr_name: Attribute name
        :return: bool
        """
        return attr_name in cls.attr_types()

    def set_default(self, attr_name):
        if self.attr_has_default_value(attr_name):
            attr_default_type = self.attr_type(attr_name)
            attr_default_value = self.get_attr_default_value(attr_name)
            delattr(self, attr_name)
            self.__annotations__[attr_name] = attr_default_type
            self.set_attribute(attr_name, None)
            self.update({attr_name: attr_default_value})

    def set_attribute(self, attr_name, value):
        if attr_name in DICT_RESERVED_KEYS:
            raise TypeError("You cannot set a reserved name as attribute")
        _store(self, attr_name, value)

    def set_attributes(self_d921dfa9_4e93_4123_893d_a7e7eb783a32, **d):
        for k, v in d.items():
            self_d921dfa9_4e93_4123_893d_a7e7eb783a32.set_attribute(k, v)

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError as exc:
            raise AttributeError(f"{type(self).__name__!r} object has no attribute {exc!s}") from None

    def __setattr__(self, name: str, value) -> None:
        self.set_attribute(name, value)

    def __delattr__(self, name: str) -> None:
        if name in DICT_RESERVED_KEYS:
            raise TypeError("You cannot delete a reserved name as attribute")
        try:
            del self[name]
        except KeyError:
            raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}") from None

    def __dir__(self):
        # keys that work as attributes, for completion in a REPL or notebook
        keys = [k for k in self.keys() if isinstance(k, str) and k.isidentifier()]
        return sorted(set(super().__dir__()) | set(keys))

    def to_dict(
        self,
        *args,
        is_recursive=False,
        exclude_none=False,
        exclude_none_in_lists=False,
        convert_list_items=False,
        **kwargs
    ):
        """
        Converts Prodict to dict.

        :param is_recursive: If True, nested Prodict attributes are converted to dicts
        :param exclude_none: If True, attributes with None values are excluded from the result
        :param exclude_none_in_lists: If True, Prodict items in lists are converted to dicts
                                      with None values excluded (legacy behavior, implies convert_list_items=True)
        :param convert_list_items: If True, Prodict items in lists are converted to dicts
                                   (respects exclude_none setting for those items)
        :return: dict

        Examples:
            # Keep list items as Prodict
            obj.to_dict()  # or to_dict(is_recursive=False, convert_list_items=False)

            # Convert list items to dict, keeping None values
            obj.to_dict(convert_list_items=True)

            # Convert list items to dict, excluding None values
            obj.to_dict(convert_list_items=True, exclude_none=True)
            # or obj.to_dict(exclude_none_in_lists=True)  # legacy, always excludes None

            # Convert everything recursively
            obj.to_dict(is_recursive=True, convert_list_items=True)
        """
        ret = {
            k: _dict_value(
                v,
                is_recursive=is_recursive,
                exclude_none=exclude_none,
                exclude_none_in_lists=exclude_none_in_lists,
                convert_list_items=convert_list_items,
            )
            for k, v in self.items()
            if _none_condition(
                v, is_recursive=is_recursive, exclude_none=exclude_none
            )
        }
        return ret
