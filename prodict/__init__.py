# Global comments:
# self is avoided to fix #15
from typing import Any, Dict, List
import copy

DICT_RESERVED_KEYS = vars(dict).keys()


class GenericMeta(type):
    pass


def _dict_value(
    v: "Prodict",
    is_recursive: bool,
    exclude_none: bool,
    exclude_none_in_lists: bool,
) -> Dict[Any, Any]:
    if is_recursive and isinstance(v, Prodict):
        return v.to_dict(is_recursive=is_recursive, exclude_none=exclude_none)
    if exclude_none_in_lists and isinstance(v, List):
        return [
            item.to_dict(exclude_none=True, is_recursive=is_recursive)
            if isinstance(item, Prodict)
            else item
            for item in v
        ]
    return v


def _none_condition(v: "Prodict", exclude_none: bool) -> bool:
    return v is not None if exclude_none else True


# noinspection PyMethodParameters
class Prodict(dict):  # type: ignore
    """
    Prodict = Dictionary with IDE friendly(auto code completion),
    dot-accessible attributes and more.
    """

    def __init__(
        self_d921dfa9_4e93_4123_893d_a7e7eb783a32,  # noqa
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        # #3: Set all properties to None
        for (
            k,
            v,
        ) in self_d921dfa9_4e93_4123_893d_a7e7eb783a32.attr_types().items():
            self_d921dfa9_4e93_4123_893d_a7e7eb783a32.set_attribute(k, None)

        # Set default values of annotated attributes
        self_d921dfa9_4e93_4123_893d_a7e7eb783a32.init()
        self_d921dfa9_4e93_4123_893d_a7e7eb783a32.set_attributes(**kwargs)

    def init(self) -> None:
        ...

    def __new__(cls, *args: Any, **kwargs: Any) -> "Prodict":
        # sourcery skip: instance-method-first-arg-name
        return super(Prodict, cls).__new__(cls, *args, **kwargs)

    def __getstate__(self) -> Dict[Any, Any]:
        return self.to_dict()

    def __setstate__(self, state: Any) -> "Prodict":
        return Prodict.from_dict(state)

    def __deepcopy__(self, memo: Any = None) -> "Prodict":
        new = self.from_dict({})
        for key in self.keys():
            new.set_attribute(key, copy.deepcopy(self[key], memo=memo))
        return new

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Prodict":
        return cls(**d)

    @classmethod
    def attr_has_default_value(cls, attr_name: str) -> bool:
        return bool(hasattr(cls, attr_name))

    @classmethod
    def get_attr_default_value(cls, attr_name: str) -> Any:
        if cls.attr_has_default_value(attr_name):
            return getattr(cls, attr_name)
        else:
            return None

    @classmethod
    def attr_type(cls, attr_name: str) -> Any:
        return cls.attr_types()[attr_name]

    @classmethod
    def attr_types(cls) -> Dict[Any, Any]:
        return cls.__annotations__ if hasattr(cls, '__annotations__') else {}

    @classmethod
    def attr_names(cls) -> List[str]:
        """
        Returns annotated attribute names
        :return: List[str]
        """
        return [k for k, v in cls.attr_types().items()]

    @classmethod
    def has_attr(cls, attr_name: str) -> bool:
        """
        Returns True if class have an annotated attribute
        :param attr_name: Attribute name
        :return: bool
        """
        return bool(cls.attr_types().get(attr_name))

    def set_default(self, attr_name: str) -> None:
        if self.attr_has_default_value(attr_name):
            attr_default_type = self.attr_type(attr_name)
            attr_default_value = self.get_attr_default_value(attr_name)
            delattr(self, attr_name)
            self.__annotations__[attr_name] = attr_default_type
            self.set_attribute(attr_name, None)
            self.update({attr_name: attr_default_value})

    def get_constructor(self, attr_name: str, value: Any) -> Any:
        """
        This method is used for type conversion.
        Prodict uses this method to get the type of a value, then based on the
        value, it return a constructor. If the type of a value is 'float' then
        it returns 'float' since 'float' is also a constructor to build a float
        value.
        """
        attr_type1 = self.attr_type(attr_name)
        constructor: Any = None
        element_type = None
        if attr_type1 == float:
            constructor = float
        elif attr_type1 == str:
            constructor = str
        elif attr_type1 == int:
            constructor = int
        elif attr_type1 == list:
            constructor = list
        elif isinstance(value, Prodict):
            constructor = attr_type1.from_dict
        elif attr_type1 is Any:
            constructor = None
        elif isinstance(value, dict):
            if attr_type1 == dict:
                constructor = Prodict.from_dict
            elif issubclass(attr_type1, Prodict):
                constructor = self.attr_type(attr_name).from_dict
        elif attr_type1 is List:
            constructor = list
        elif hasattr(attr_type1, '__origin__'):
            if attr_type1.__dict__['__origin__'] is list:
                # if the type is 'List[something]'
                if len(attr_type1.__args__) == 0:
                    constructor = list
                elif len(attr_type1.__args__) == 1:
                    constructor = List
                    element_type = attr_type1.__args__[0]
                elif len(attr_type1.__args__) > 1:
                    raise TypeError('Only one dimensional List is supported')
            elif attr_type1.__dict__['__origin__'] is tuple:
                # if the type is 'Tuple[something]'
                constructor = tuple

        # print('constr={} element_type={}'.format(constructor, element_type))
        return constructor, element_type

    def set_attribute(self, attr_name: str, value: Any) -> None:
        # sourcery skip: merge-else-if-into-elif, move-assign-in-block
        if attr_name in DICT_RESERVED_KEYS:
            raise TypeError("You cannot set a reserved name as attribute")
        if self.has_attr(attr_name):
            if value is None:
                self.update({attr_name: None})
            elif self.attr_type(attr_name) == Any:
                self[attr_name] = value
            else:
                constructor, element_type = self.get_constructor(
                    attr_name, value
                )
                if constructor is None:
                    self.update({attr_name: value})
                elif constructor == List:
                    value_list: List[element_type] = value  # type: ignore
                    new_list: List[element_type] = []  # type: ignore

                    if issubclass(element_type, Prodict):
                        element_constructor = element_type.from_dict
                    else:
                        element_constructor = element_type

                    new_list.extend(element_constructor(v) for v in value_list)
                    self.update({attr_name: new_list})
                elif constructor == list:
                    self.update({attr_name: list(value)})
                else:
                    self.update({attr_name: constructor(value)})
        else:
            if isinstance(value, dict):
                if isinstance(value, Prodict):
                    constructor = value.from_dict
                else:
                    constructor = Prodict.from_dict
                self.update({attr_name: constructor(value)})
            else:
                self.update({attr_name: value})

    def set_attributes(
        self_d921dfa9_4e93_4123_893d_a7e7eb783a32, **d: Any  # noqa
    ) -> None:  # sourcery skip: instance-method-first-arg-name
        for k, v in d.items():
            self_d921dfa9_4e93_4123_893d_a7e7eb783a32.set_attribute(k, v)

    def __getattr__(self, item: str) -> Any:
        return self[item]

    def __setattr__(self, name: str, value: Any) -> None:
        self.set_attribute(name, value)

    def to_dict(
        self,
        *args: Any,
        is_recursive: bool = False,
        exclude_none: bool = False,
        exclude_none_in_lists: bool = False,
        **kwargs: Any,
    ) -> Dict[Any, Any]:
        return {
            k: _dict_value(
                v,
                is_recursive=is_recursive,
                exclude_none=exclude_none,
                exclude_none_in_lists=exclude_none_in_lists,
            )
            for k, v in self.items()
            if _none_condition(v, exclude_none=exclude_none)
        }
