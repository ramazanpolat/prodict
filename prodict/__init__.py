from typing import Any, List, TypeVar, Tuple
import copy

# from typing_inspect import get_parameters

DICT_RESERVED_KEYS = vars(dict).keys()


class GenericMeta(type):
    pass


class Prodict(dict):
    """
    Prodict = Dictionary with IDE friendly(auto code completion), dot-accessible attributes and more.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set default values of annotated attributes
        # for k, v in self.attr_types().items():
        #     if self.attr_has_default_value(k):
        #         self.set_default(k)
        self.set_attributes(**kwargs)
        self.init()

    def init(self):
        ...

    def __deepcopy__(self, memo=None):
        print("__deepcopy__ type(self):", type(self))
        new = self.from_dict({})
        for key in self.keys():
            new.set_attribute(key, copy.deepcopy(self[key], memo=memo))
        return new
        # return copy.deepcopy(self.from_dict(self.to_dict()), memo=memo)

    @classmethod
    def from_dict(cls, d: dict):
        val: cls = cls(**d)
        return val  # type: cls

    @classmethod
    def attr_has_default_value(cls, attr_name: str) -> bool:
        if hasattr(cls, attr_name):
            return True
        return False

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
        return cls.__annotations__ if hasattr(cls, '__annotations__') else {}
        # if hasattr(cls, '__annotations__'):
        #     return cls.__annotations__
        # return {}

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

    def get_constructor(self, attr_name, value):
        attr_type1 = self.attr_type(attr_name)
        constructor = None
        element_type = None
        # print('     attr_name="{}" attr_type={} value={}'.format(attr_name, attr_type1, value))
        # print("attr_type1:", attr_type1)
        # print("type(attr_type1):", type(attr_type1))
        # print(dir(attr_type1))
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
            # if the type is 'List'
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
                    raise TypeError('Only one dimensional List is supported, like List[str], List[int], List[Prodict]')
            elif attr_type1.__dict__['__origin__'] is tuple:
                # if the type is 'Tuple[something]'
                constructor = tuple

        # print('     constructor={} element_type={}'.format(constructor, element_type))
        return constructor, element_type

    def set_attribute(self, attr_name, value):
        if attr_name in DICT_RESERVED_KEYS:
            raise TypeError("You cannot set a reserved name as attribute")
        if self.has_attr(attr_name):
            if value is None:
                self.update({attr_name: None})
            elif self.attr_type(attr_name) == Any:
                self[attr_name] = value
            else:
                constructor, element_type = self.get_constructor(attr_name, value)
                if constructor is None:
                    self.update({attr_name: value})
                elif constructor == List:
                    value_list: List[element_type] = value
                    new_list: List[element_type] = []

                    if issubclass(element_type, Prodict):
                        element_constructor = element_type.from_dict
                    else:
                        element_constructor = element_type

                    for v in value_list:
                        new_list.append(element_constructor(v))
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

    # def set_attribute(self, attr_name, value):
    #     if self.has_attr(attr_name):
    #         if value is None:
    #             self.update({attr_name: None})
    #         elif self.attr_type(attr_name) == Any:
    #             self[attr_name] = value
    #         elif isinstance(value, Prodict):
    #             constructor = self.attr_type(attr_name)
    #             self.update({attr_name: constructor.from_dict(value.to_dict())})
    #         elif isinstance(value, dict):
    #             constructor = self.attr_type(attr_name)
    #             if constructor == dict:
    #                 self.update({attr_name: Prodict.from_dict(value)})
    #             # elif constructor == List:
    #             #     if len(constructor.__args__) != 1:
    #             #         raise TypeError('Only one dimensional List is supported')
    #             #     constructor = constructor.__args__[0]
    #             #     value  # type: List[constructor]
    #             #     final_list: List[constructor] = []
    #             #     for elem in value:
    #             else:
    #                 self.update({attr_name: constructor.from_dict(value)})
    #         else:
    #             self.update({attr_name: self.attr_type(attr_name)(value)})
    #     else:
    #         self[attr_name] = value

    def set_attributes(self, **d):
        for k, v in d.items():
            self.set_attribute(k, v)

    def __getattr__(self, item):
        # print('__getattr__("{}")'.format(item))
        return self.get(item, None)

    # def __getattribute__(self, item):
    #     print('__getattribute__("{}")'.format(item))
    #     if item == '__annotations__':
    #         return self.__annotations__
    #     return self.__getattr__(item)

    def __setattr__(self, name: str, value) -> None:
        self.set_attribute(name, value)

    def to_dict(self):
        return dict(self)
