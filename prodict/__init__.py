# Global comments:
# self is avoided to fix #15
from typing import Any, List, Union, get_args, get_origin, get_type_hints
import copy
import typing
import weakref

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

# conversions that may fail on a value; the value is then stored as given
_CONVERSION_ERRORS = (TypeError, ValueError, OverflowError)

# annotations per class, collected over the class hierarchy
_attr_types_cache = weakref.WeakKeyDictionary()


def _own_annotations(klass):
    # the annotations a class declares itself, unevaluated where they cannot be
    if annotationlib is not None:
        return annotationlib.get_annotations(klass, format=annotationlib.Format.FORWARDREF)
    return klass.__dict__.get('__annotations__', {})


def _try(constructor, value):
    try:
        return constructor(value)
    except _CONVERSION_ERRORS:
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
            return Prodict.from_dict(value)
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
            return [_convert(args[0], item) for item in items]
        return items
    if origin is tuple:
        # Tuple, Tuple[...] and tuple[...]; items are not converted
        if isinstance(value, dict):
            return value
        return _try(tuple, value)
    # bool, plain tuple, other classes, string annotations that could not be
    # resolved, and anything else: stored as given
    return value


def _none_condition(v, is_recursive, exclude_none):
    return v is not None if exclude_none else True


# noinspection PyMethodParameters
class Prodict(dict):
    """
    Prodict = Dictionary with IDE friendly(auto code completion),
    dot-accessible attributes and more.
    """

    def __init__(self_d921dfa9_4e93_4123_893d_a7e7eb783a32, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # #55: annotated values that arrived in a positional dict (or iterable
        # of pairs). Read them back from the dict itself, since args may be a
        # one-shot iterator, so they survive the reset below and get converted.
        positional = {
            k: self_d921dfa9_4e93_4123_893d_a7e7eb783a32[k]
            for k in self_d921dfa9_4e93_4123_893d_a7e7eb783a32.attr_types()
            if k in self_d921dfa9_4e93_4123_893d_a7e7eb783a32 and k not in kwargs
        }

        # #3: Set all properties to None
        for (
            k,
            v,
        ) in self_d921dfa9_4e93_4123_893d_a7e7eb783a32.attr_types().items():
            self_d921dfa9_4e93_4123_893d_a7e7eb783a32.set_attribute(k, None)

        # Set default values of annotated attributes
        self_d921dfa9_4e93_4123_893d_a7e7eb783a32.init()
        for k, v in positional.items():
            self_d921dfa9_4e93_4123_893d_a7e7eb783a32.set_attribute(k, v)
        self_d921dfa9_4e93_4123_893d_a7e7eb783a32.set_attributes(**kwargs)

    def init(self):
        ...

    def __new__(cls, *args, **kwargs):
        return super(Prodict, cls).__new__(cls, *args, **kwargs)

    def __getstate__(self):
        return self.to_dict()

    def __setstate__(self, state):
        return Prodict.from_dict(state)

    def __deepcopy__(self, memo=None):
        new = self.from_dict({})
        for key in self.keys():
            new.set_attribute(key, copy.deepcopy(self[key], memo=memo))
        return new

    @classmethod
    def from_dict(cls, d: dict):
        return cls(**d)

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
        annotations are resolved where possible.
        """
        types = _attr_types_cache.get(cls)
        if types is None:
            try:
                types = get_type_hints(cls)
            except Exception:
                # an annotation that cannot be resolved, such as a forward
                # reference to a class defined later: use them as written
                types = {}
                for klass in reversed(cls.__mro__):
                    types.update(_own_annotations(klass))
            _attr_types_cache[cls] = types
        return types

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
        return bool(cls.attr_types().get(attr_name))

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
        if self.has_attr(attr_name):
            value = _convert(self.attr_type(attr_name), value)
        elif isinstance(value, dict):
            if isinstance(value, Prodict):
                value = value.from_dict(value)
            else:
                value = Prodict.from_dict(value)
        self.update({attr_name: value})

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
