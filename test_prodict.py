import contextlib
import pickle
from unittest import TestCase
from typing import List, Any, Dict, Tuple
from prodict import Prodict
import copy


class Dad(Prodict):
    name: str
    age: int


class Son(Prodict):
    father: Dad
    age: int
    name: str


class Ram(Prodict):
    brand: str
    capacity: int
    unit: str


class CpuCore(Prodict):
    threads: int
    clock: float
    unit: str


class Cpu(Prodict):
    brand: str
    model: str
    cache: int
    cores: List[CpuCore]


class Computer(Prodict):
    brand: str
    cpu: Cpu
    rams: List[Ram]
    dict_key: dict  # type: ignore
    uninitialized: str
    rams2: List[Ram]

    def total_ram(self) -> int:  # sourcery skip: comprehension-to-generator
        return sum([ram.capacity for ram in self.rams])

    def total_ram2(self) -> int:  # sourcery skip: comprehension-to-generator
        if 'rams2' in self and self['rams2'] is not None:
            return sum([ram.capacity for ram in self.rams2])
        return 0


class AnyType(Prodict):
    a: Any
    b: Tuple[Any]
    c: Any


class SimpleKeyValue(Prodict):
    int_key: int
    str_key: str
    float_key: float


class SimpleKeyDefaultValue(Prodict):
    int_key: int = 1
    str_key: str = 'default str'
    float_key: float = 1.234


class AdvancedKeyValue(Prodict):
    tuple_key: Tuple[Any]
    list_key: List[Any]
    dict_key: Dict[Any, Any]


class ListProdict(Prodict):
    li: List[Any]
    li_str: List[str]
    li_int: List[int]


class Recursive(Prodict):
    prodict_key: Prodict
    simple_key: SimpleKeyValue


class TestProdict(TestCase):
    def test_deep_recursion_from_dict(self) -> None:
        computer_dict = {
            'x_str': 'string',
            'x_int': 0,
            'x_float': 1.234,
            'dict_key': {'info': 'This must be a dict'},
            'brand': 'acme',
            'rams': [
                {'brand': 'Kingston', 'capacity': 4, 'unit': 'GB'},
                {'brand': 'Samsung', 'capacity': 8, 'unit': 'GB'},
            ],
            'cpu': {
                'brand': 'Intel',
                'model': 'i5-4670',
                'cache': 3,
                'cores': [
                    {'threads': 2, 'clock': 3.4, 'unit': 'GHz'},
                    {'threads': 4, 'clock': 3.1, 'unit': 'GHz'},
                ],
            },
        }

        computer = Computer.from_dict(computer_dict)
        assert type(computer) == Computer
        assert type(computer.dict_key) == Prodict
        assert type(computer.brand) == str
        assert type(computer.cpu) == Cpu
        assert type(computer.rams) == list
        assert type(computer.rams[0]) == Ram

    def test_bracket_access(self) -> None:
        pd = SimpleKeyValue()
        pd.str_key = 'str_value_123'
        assert pd['str_key'] == pd.str_key
        assert pd.get('str_key') == pd.str_key

    def test_null_assignment(self) -> None:
        pd = SimpleKeyValue()

        pd.str_key = 'str1'
        assert pd.str_key == 'str1'

        pd.str_key = None  # type: ignore
        assert pd.str_key is None

        pd.dynamic_int = 1
        assert pd.dynamic_int == 1

        pd.dynamic_int = None
        assert pd.dynamic_int is None

        pd.dynamic_str = 'str'
        assert pd.dynamic_str == 'str'

        pd.dynamic_str = None
        assert pd.dynamic_str is None

    def test_multiple_instances(self) -> None:
        class Multi(Prodict):
            a: int

        m1 = Multi()
        m1.a = 1

        m2 = Multi()
        m2.a = 2

        assert m2.a == m1.a + 1

    def test_property(self) -> None:
        class PropertyClass(Prodict):
            first: int
            second: int

            @property
            def diff(self) -> float:
                return abs(self.second - self.first)

        first = 1
        second = 2
        pc = PropertyClass(first=first, second=second)
        assert pc.diff == abs(second - first)

    def test_use_defaults_method(self) -> None:
        class WithDefault(Prodict):
            a: int
            b: str

            def init(self) -> None:
                self.a = 1
                self.b = 'string'

        wd = WithDefault()
        assert wd.a == 1
        assert wd.b == 'string'

    def test_type_conversion(self) -> None:
        class TypeConversionClass(Prodict):
            an_int: int
            a_str: str
            a_float: float

        assert TypeConversionClass(an_int='1').an_int == 1
        assert TypeConversionClass(an_int=1).an_int == 1
        assert TypeConversionClass(a_str='str').a_str == 'str'
        assert TypeConversionClass(a_float=123.45).a_float == 123.45
        assert TypeConversionClass(a_float='123.45').a_float == 123.45

    def test_deepcopy1(self) -> None:
        root_node = Prodict(number=1, data="ROOT node", next=None)
        copied = copy.deepcopy(root_node)

        # have same dict
        assert copied == root_node
        # have different id
        assert copied is not root_node
        # have same type
        assert type(root_node) is type(copied)

    def test_deepcopy2(self) -> None:
        class MyLinkListNode(Prodict):
            number: int
            data: Any
            next: Prodict

        root_node = MyLinkListNode(number=1, data="ROOT node", next=None)
        copied = copy.deepcopy(root_node)

        # have same dict
        assert copied == root_node
        # have different id
        assert copied is not root_node
        # have same type
        assert type(root_node) is type(copied)

    def test_unknown_attr(self) -> None:
        ram = Ram.from_dict({'brand': 'Samsung', 'capacity': 4, 'unit': 'YB'})
        print(ram.brand)  # Ok

        # Should fail
        with contextlib.suppress(KeyError):
            print(ram['flavor'])
            assert False
        # Should fail
        with contextlib.suppress(KeyError):
            print(ram.flavor)
            assert False

    def test_default_none(self) -> None:  # sourcery skip: raise-specific-error
        class Car(Prodict):
            brand: str
            year: int

        honda = Car(brand='Honda')
        print('honda.year:', honda.year)
        assert honda.year is None
        try:
            print(
                honda.color
            )  # This also raises KeyError since it is not even defined or set.
            raise Exception("'honda.color' must raise KeyError")
        except KeyError:
            print("'honda.color' raises KeyError. Ok")

    def test_to_dict_recursive(self) -> None:
        dad = Dad(name='Bob')
        son = Son(name='Jeremy', father=dad)
        assert type(son.to_dict(is_recursive=False)['father']) == Dad
        assert type(son.to_dict(is_recursive=True)['father']) == dict

    def test_to_dict_exclude_none(self) -> None:
        dad = Dad(name='Bob')
        son = Son(name='Jeremy', father=dad)

        assert 'age' in son.to_dict()
        assert 'age' not in son.to_dict(exclude_none=True)

        assert 'age' in son.to_dict()['father']
        assert (
            'age'
            not in son.to_dict(is_recursive=True, exclude_none=True)['father']
        )

    def test_to_dict_exclude_none_for_list_elements(self) -> None:
        class MyEntry(Prodict):
            some_str: str
            some_dict: Prodict

        class ModelConfig(Prodict):
            my_list: List[MyEntry]
            my_var: str

        data = {
            "my_list": [
                {
                    "some_str": "Hello",
                    "some_dict": {
                        "name": "Frodo",
                    },
                },
                {"some_str": "World"},
            ],
            "my_var": None,
        }

        model = ModelConfig.from_dict(data)
        d1 = model.to_dict(
            exclude_none=True, is_recursive=False, exclude_none_in_lists=True
        )
        assert 'my_var' not in d1
        assert 'some_dict' not in d1['my_list'][1]

        d2 = model.to_dict(exclude_none=True, exclude_none_in_lists=False)
        assert 'my_var' not in d2
        assert 'some_dict' in d2['my_list'][1]

        d2 = model.to_dict(exclude_none_in_lists=True)
        assert 'my_var' in d2
        assert 'some_dict' not in d2['my_list'][1]

    def test_issue12(self) -> None:
        class Comment(Prodict):
            user_id: int
            comment: str
            date: str

        class Post(Prodict):
            title: str
            text: str
            date: str
            comments: List[Comment]

        class User(Prodict):
            user_id: int
            user_name: str
            posts: List[Post]

        json1 = {
            "user_id": 1,
            "user_name": "rambo",
            "posts": [
                {
                    "title": "Hello World",
                    "text": "This is my first blog post...",
                    "date": "2018-01-02 03:04:05",
                    "comments": [
                        {
                            "user_id": 2,
                            "comment": "Good to see you blogging",
                            "date": "2018-01-02 03:04:06",
                        },
                        {
                            "user_id": 3,
                            "comment": "Good for you",
                            "date": "2018-01-02 03:04:07",
                        },
                    ],
                },
                {
                    "title": "Hello World 2",
                    "text": "This is my first blog post...",
                    "date": "2018-01-02 03:04:05",
                    "comments": [
                        {
                            "user_id": 2,
                            "comment": "Good to see you blogging",
                            "date": "2018-01-02 03:04:06",
                        },
                        {
                            "user_id": 3,
                            "comment": "Good for you",
                            "date": "2018-01-02 03:04:07",
                        },
                    ],
                },
            ],
        }

        p = User.from_dict(json1)
        assert len(p.posts) == 2
        assert type(p.posts[0].title) == str

    def test_issue15(self) -> None:
        """url: https://github.com/ramazanpolat/prodict/issues/15
        if the payload has a attribute named 'self' then we get a TypeError:
            TypeError: __init__() got multiple values for argument 'self'

        """
        try:
            Prodict(self=1)
            assert True
        except TypeError:
            assert False

    def test_accept_generator(self) -> None:
        """
        https://github.com/ramazanpolat/prodict/issues/18
        """
        s = ';O2Sat:92;HR:62;RR:0'

        # this works
        # dd1 = dict(x.split(':') for x in s.split(';') if ':' in x)

        # this fails with
        # TypeError: __init__() takes 1 positional argument but 2 were given
        pd1 = Prodict(x.split(':') for x in s.split(';') if ':' in x)
        print(pd1)
        assert True

    def test_pickle(self) -> None:
        try:
            encoded = pickle.dumps(Prodict(a=42))
            decoded = pickle.loads(encoded)
            assert decoded.a == 42
        except Exception:
            assert False
