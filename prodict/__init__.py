import inspect
from typing import Any, List, TypeVar, Tuple

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

        # merge class attributes and annotated kwargs
        class_attrs = self.get_class_attrs()
        class_attrs.update(kwargs)

        print(class_attrs)

        # Set default values of annotated attributes
        for k, v in class_attrs.items():
            # print(k)
            self.set_attribute(str(k), v)
        # for k, v in self.anno_types().items():
        #     if self.attr_has_default_value(k):
        #         print(k, v, self.get_attr_default_value(k))
        #         self.set_attribute(k, self.get_attr_default_value(k))
        # set provided attributes
        # self.set_attributes(**kwargs)

    @classmethod
    def get_class_attrs(cls):
        members = inspect.getmembers(cls, lambda a: not (inspect.isroutine(a)))
        return {a[0]: a[1] for a in members if not (a[0].startswith('__') and a[0].endswith('__'))}

    @classmethod
    def from_dict(cls, d: dict):
        val: cls = cls(**d)
        return val  # type: cls

    # @classmethod
    # def attr_has_default_value(cls, attr_name: str) -> bool:
    #     return True if hasattr(cls, attr_name) else False
    #     # if hasattr(cls, attr_name):
    #     #     return True
    #     # return False

    # @classmethod
    # def get_attr_default_value(cls, attr_name: str):
    #     if cls.attr_has_default_value(attr_name):
    #         return getattr(cls, attr_name)
    #     else:
    #         return None

    @classmethod
    def anno_type(cls, attr_name: str):
        return cls.anno_types()[attr_name]

    @classmethod
    def anno_types(cls):
        return cls.__annotations__ if hasattr(cls, '__annotations__') else {}
        # if hasattr(cls, '__annotations__'):
        #     return cls.__annotations__
        # return {}

    @classmethod
    def anno_names(cls) -> List[str]:
        """
        Returns annotated attribute names
        :return: List[str]
        """
        return list(cls.anno_types().keys())
        # return [k for k, v in cls.anno_types().items()]

    @classmethod
    def has_attr(cls, attr_name: str):
        """
        Returns True if class have an annotated attribute
        :param attr_name: Attribute name
        :return: bool
        """
        result = bool(cls.anno_types().get(attr_name))
        print(f'hasattr(cls, "{attr_name}")={result}')
        # return hasattr(cls, attr_name)
        # class_attrs = cls.get_class_attrs()
        # class_attrs.update()
        return result

    # def set_default(self, anno_name):
    #     """
    #     NOT USED
    #     :param anno_name:
    #     :return:
    #     """
    #     if self.attr_has_default_value(anno_name):
    #         attr_default_type = self.anno_type(anno_name)
    #         attr_default_value = self.get_attr_default_value(anno_name)
    #         delattr(self, anno_name)
    #         self.__annotations__[anno_name] = attr_default_type
    #         self.set_attribute(anno_name, None)
    #         self.update({anno_name: attr_default_value})

    def get_constructor(self, anno_name, value):
        constructor = None
        element_type = None
        anno_type = self.anno_type(anno_name)
        # print('     attr_name="{}" attr_type={} value={}'.format(attr_name, attr_type1, value))
        # print("attr_type1:", attr_type1)
        # print("type(attr_type1):", type(attr_type1))
        # print(dir(attr_type1))
        if anno_type == list:
            constructor = list
        elif isinstance(value, Prodict):
            print("{attr_name}({value}) is instance of Prodict")
            constructor = anno_type.from_dict
        elif anno_type is Any:
            constructor = None
        elif isinstance(value, dict):
            if anno_type == dict:
                constructor = Prodict.from_dict
            elif issubclass(anno_type, Prodict):
                constructor = self.anno_type(anno_name).from_dict
        elif anno_type is List:
            # if the type is 'List'
            constructor = list
        elif hasattr(anno_type, '__origin__'):
            if anno_type.__dict__['__origin__'] is list:
                # if the type is 'List[]' or 'List[some_type]'
                if len(anno_type.__args__) == 0:
                    # it is 'List[]'
                    constructor = list
                elif len(anno_type.__args__) == 1:
                    # it is 'List[some_type]'
                    constructor = List
                    # this is 'some_type'
                    element_type = anno_type.__args__[0]
                elif len(anno_type.__args__) > 1:
                    raise TypeError('Only one dimensional List is supported, like List[str], List[int], List[Prodict]')
            elif anno_type.__dict__['__origin__'] is tuple:
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
            elif self.anno_type(attr_name) == Any:
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

    # def __getattribute__(self, item):
    #     print(f'__getattribute__({item})')
    #     if self.has_attr(item):
    #         return self.to_dict().get(item, None)
    #     return 'XYZ'

    def __getitem__(self, item):
        if self.has_attr(item):
            return self.get(item, None)

    # def __getattr__(self, item):
    #     print(f'__getattr__({item})')
    #     return self.to_dict().get(item, None)

    # def __getattribute__(self, item):
    #     print('__getattribute__("{}")'.format(item))
    #     if item == '__annotations__':
    #         return self.__annotations__
    #     return self.__getattr__(item)

    def __setattr__(self, name: str, value) -> None:
        self.set_attribute(name, value)

    def to_dict(self):
        return dict(self)
