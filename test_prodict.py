import __future__
import functools
import gc
import pickle
import threading
import weakref
import sys
import types
from decimal import Decimal
from unittest import mock
from unittest import TestCase
from typing import List, Any, Tuple, Dict, Optional, Union, TypedDict
import unittest
from datetime import datetime
import prodict
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
    dict_key: dict
    uninitialized: str
    rams2: List[Ram]

    def total_ram(self):
        return sum([ram.capacity for ram in self.rams])

    def total_ram2(self):
        if 'rams2' in self and self['rams2'] is not None:
            return sum([ram.capacity for ram in self.rams2])
        return 0


class AnyType(Prodict):
    # x=1 type: Any
    a: Any
    b: Tuple
    c: Any


class SimpleKeyValue(Prodict):
    int_key: int
    str_key: Optional[str]  # #8: lets type checkers accept None
    float_key: float


class SimpleKeyDefaultValue(Prodict):
    int_key: int = 1
    str_key: str = 'default str'
    float_key: float = 1.234


class AdvancedKeyValue(Prodict):
    tuple_key: tuple
    list_key: list
    dict_key: dict


class ListProdict(Prodict):
    li: List
    li_str: List[str]
    li_int: List[int]


def make_module(name, source, future_annotations=False):
    # runs source as a real module, so that class bodies and annotation
    # resolution behave as they do in user code
    module = types.ModuleType(name)
    sys.modules[name] = module
    flags = __future__.annotations.compiler_flag if future_annotations else 0
    exec(compile(source, name, 'exec', flags=flags, dont_inherit=True), module.__dict__)
    return module


class Counter(Prodict):
    # module level, so that pickle can find it
    n: int
    log: List[str]
    init_calls = []

    def init(self):
        Counter.init_calls.append(1)
        self.log = ['created']


class Slotted(Prodict):
    __slots__ = ('tag', '__secret')


class Strict(Prodict):
    # a subclass with its own constructor, keyword arguments only
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Positional(Prodict):
    # a subclass with its own constructor that takes the data positionally
    def __init__(self, data):
        super().__init__(data)


class Point(Prodict):
    # a subclass with its own __new__ arguments and state hooks
    def __new__(cls, x, y):
        return super().__new__(cls)

    def __init__(self, x, y):
        super().__init__(x=x, y=y)

    def __getnewargs__(self):
        return self['x'], self['y']


class Session(Prodict):
    def __getstate__(self):
        return {'token': None}  # never save the token


class ForwardNode(Prodict):
    # string annotations, as with `from __future__ import annotations`
    value: 'int'
    children: 'List[ForwardNode]'


class UnresolvedRef(Prodict):
    later: 'NoSuchClass'  # noqa: F821
    n: int


class Recursive(Prodict):
    prodict_key: Prodict
    simple_key: SimpleKeyValue


class TestProdict(TestCase):
    def test_deep_recursion_from_dict(self):
        computer_dict = {
            'x_str': 'string',
            'x_int': 0,
            'x_float': 1.234,
            'dict_key': {'info': 'This must be a dict'},
            'brand': 'acme',
            'rams': [
                {
                    'brand': 'Kingston',
                    'capacity': 4,
                    'unit': 'GB'
                },
                {
                    'brand': 'Samsung',
                    'capacity': 8,
                    'unit': 'GB'

                }],
            'cpu': {
                'brand': 'Intel',
                'model': 'i5-4670',
                'cache': 3,
                'cores': [
                    {
                        'threads': 2,
                        'clock': 3.4,
                        'unit': 'GHz'
                    },
                    {
                        'threads': 4,
                        'clock': 3.1,
                        'unit': 'GHz'
                    }
                ]
            }
        }

        computer: Computer = Computer.from_dict(computer_dict)
        # print('computer =', computer)
        assert type(computer) == Computer
        # print('type(computer.dict_key) =', type(computer.dict_key))
        assert type(computer.dict_key) == Prodict
        # print('computer.brand =', computer.brand)
        assert type(computer.brand) == str
        # print('computer.cpu =', computer.cpu)
        assert type(computer.cpu) == Cpu
        # print('type(computer.rams) =', type(computer.rams))
        assert type(computer.rams) == list
        # print('computer.rams[0] =', computer.rams[0])
        assert type(computer.rams[0]) == Ram
        print('Total ram =', computer.total_ram())
        print('Total ram2 =', computer.total_ram2())
        print("computer['rams'] =", computer['rams'])
        print("type(computer['rams']) =", type(computer['rams']))
        print("computer['rams'][0] =", computer['rams'][0])

    def test_bracket_access(self):
        pd = SimpleKeyValue()
        pd.str_key = 'str_value_123'
        assert pd['str_key'] == pd.str_key
        assert pd.get('str_key') == pd.str_key

    def test_null_assignment(self):
        pd = SimpleKeyValue()

        pd.str_key = 'str1'
        assert pd.str_key == 'str1'

        pd.str_key = None
        assert pd.str_key is None

        pd.dynamic_int = 1
        assert pd.dynamic_int == 1

        pd.dynamic_int = None
        assert pd.dynamic_int is None

        pd.dynamic_str = 'str'
        assert pd.dynamic_str == 'str'

        pd.dynamic_str = None
        assert pd.dynamic_str is None

    def test_multiple_instances(self):
        class Multi(Prodict):
            a: int

        m1 = Multi()
        m1.a = 1

        m2 = Multi()
        m2.a = 2

        assert m2.a == m1.a + 1

    def test_property(self):
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

    def test_use_defaults_method(self):
        class WithDefault(Prodict):
            a: int
            b: str

            def init(self):
                self.a = 1
                self.b = 'string'

        wd = WithDefault()
        assert wd.a == 1
        assert wd.b == 'string'

    def test_type_conversion(self):
        class TypeConversionClass(Prodict):
            an_int: int
            a_str: str
            a_float: float

        assert TypeConversionClass(an_int='1').an_int == 1
        assert TypeConversionClass(an_int=1).an_int == 1
        assert TypeConversionClass(a_str='str').a_str == 'str'
        assert TypeConversionClass(a_float=123.45).a_float == 123.45
        assert TypeConversionClass(a_float='123.45').a_float == 123.45

    def test_deepcopy1(self):
        root_node = Prodict(number=1, data="ROOT node", next=None)

        copied = copy.deepcopy(root_node)

        print("--root-node id:", id(root_node))
        print(root_node)
        print("--copied id:", id(copied))
        print(copied)
        print("--root_node.data")
        print(type(root_node))
        print(root_node.data)
        print("--copied.data")
        print(type(copied))
        print(copied.data)

        # have same dict
        assert copied == root_node
        # have different id
        assert copied is not root_node
        # have same type
        assert type(root_node) is type(copied)

    def test_deepcopy2(self):
        class MyLinkListNode(Prodict):
            number: int
            data: Any
            next: Prodict

        root_node = MyLinkListNode(number=1, data="ROOT node", next=None)
        # node1 = MyLinkListNode(number=2, data="1st node", next=None)
        # root_node.next = node1

        copied = copy.deepcopy(root_node)
        # copied.number += 1

        print("--root-node id:", id(root_node))
        print(root_node)
        print("--copied id:", id(copied))
        print(copied)
        print("--root_node.data")
        print(type(root_node))
        print(root_node.data)
        print("--copied.data")
        print(type(copied))
        print(copied.data)

        # have same dict
        assert copied == root_node
        # have different id
        assert copied is not root_node
        # have same type
        assert type(root_node) is type(copied)

    def test_unknown_attr(self):
        ram = Ram.from_dict({'brand': 'Samsung', 'capacity': 4, 'unit': 'YB'})
        print(ram.brand)  # Ok

        # Should fail
        try:
            print(ram['flavor'])
            assert False
        except KeyError:
            pass

        # Should fail
        try:
            print(ram.flavor)
            assert False
        except AttributeError:
            pass

    def test_default_none(self):
        class Car(Prodict):
            brand: str
            year: int

        honda = Car(brand='Honda')
        print('honda.year:', honda.year)
        assert honda.year is None
        try:
            print(honda.color)  # This also raises KeyError since it is not even defined or set.
            raise Exception("'honda.color' must raise AttributeError")
        except AttributeError:
            print("'honda.color' raises AttributeError. Ok")

    def test_to_dict_recursive(self):
        dad = Dad(name='Bob')
        son = Son(name='Jeremy', father=dad)

        # print('dad dict:', dad.to_dict())
        # print('--')
        # print('son dict:', son.to_dict())
        # print('--')

        # print(type(son.to_dict(is_recursive=False)['father']))
        assert type(son.to_dict(is_recursive=False)['father']) == Dad
        # print(type(son.to_dict(is_recursive=True)['father']))
        assert type(son.to_dict(is_recursive=True)['father']) == dict

    def test_to_dict_exclude_none(self):
        dad = Dad(name='Bob')
        son = Son(name='Jeremy', father=dad)

        assert 'age' in son.to_dict()
        assert 'age' not in son.to_dict(exclude_none=True)

        assert 'age' in son.to_dict()['father']
        assert 'age' not in son.to_dict(is_recursive=True, exclude_none=True)['father']

        print('exclude_none=False:', son.to_dict(exclude_none=False))
        print('exclude_none=True:', son.to_dict(exclude_none=True))

        print('exclude_none=False:', son.to_dict(exclude_none=False, is_recursive=True))
        print('exclude_none=True:', son.to_dict(exclude_none=True, is_recursive=True))

        print(type(son.to_dict()['father'].to_dict()))

    def test_to_dict_exclude_none_for_list_elements(self):
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
                    }
                },
                {
                    "some_str": "World"
                }
            ],
            "my_var": None
        }

        model = ModelConfig.from_dict(data)
        d1 = model.to_dict(exclude_none=True, is_recursive=False, exclude_none_in_lists=True)
        print(d1)
        assert 'my_var' not in d1
        assert 'some_dict' not in d1['my_list'][1]

        d2 = model.to_dict(exclude_none=True, exclude_none_in_lists=False)

        print(d2)
        assert 'my_var' not in d2
        assert 'some_dict' in d2['my_list'][1]

        d2 = model.to_dict(exclude_none_in_lists=True)

        print(d2)
        assert 'my_var' in d2
        assert 'some_dict' not in d2['my_list'][1]





    def test_issue12(self):
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
                            "date": "2018-01-02 03:04:06"
                        },
                        {
                            "user_id": 3,
                            "comment": "Good for you",
                            "date": "2018-01-02 03:04:07"
                        }
                    ]
                },
                {
                    "title": "Hello World 2",
                    "text": "This is my first blog post...",
                    "date": "2018-01-02 03:04:05",
                    "comments": [
                        {
                            "user_id": 2,
                            "comment": "Good to see you blogging",
                            "date": "2018-01-02 03:04:06"
                        },
                        {
                            "user_id": 3,
                            "comment": "Good for you",
                            "date": "2018-01-02 03:04:07"
                        }
                    ]
                }
            ]
        }

        p = User.from_dict(json1)
        assert len(p.posts) == 2
        assert type(p.posts[0].title) == str

    def test_issue15(self):
        """url: https://github.com/ramazanpolat/prodict/issues/15
        if the payload has a attribute named 'self' then we get a TypeError:
            TypeError: __init__() got multiple values for argument 'self'

        """
        try:
            p = Prodict(self=1)
            assert True
        except TypeError:
            assert False

    def test_accept_generator(self):
        """
        https://github.com/ramazanpolat/prodict/issues/18
        """
        s = ';O2Sat:92;HR:62;RR:0'

        # this works
        dd1 = dict(x.split(':') for x in s.split(';') if ':' in x)

        # this fails with TypeError: __init__() takes 1 positional argument but 2 were given
        pd1 = Prodict(x.split(':') for x in s.split(';') if ':' in x)
        print(pd1)
        assert True

    def test_pickle(self):
        try:
            encoded = pickle.dumps(Prodict(a=42))
            decoded = pickle.loads(encoded)
            assert decoded.a == 42
            # p = Prodict(a=1, b=2)
            # encoded = pickle.dumps(p)
            # print(encoded)
            # decoded = pickle.loads(encoded)
            # print(decoded)
        except:
            assert False

    def test_dict_value_all_combinations(self):
        """
        Test to_dict method with all 8 combinations of the original three boolean parameters:
        is_recursive, exclude_none, exclude_none_in_lists

        Expected behavior:
        - is_recursive=True: converts nested Prodict attributes to plain dicts
        - exclude_none=True: excludes key-value pairs where value is None
        - exclude_none_in_lists=True: converts list items to dict AND excludes None values (legacy behavior)
        """
        from prodict import _dict_value

        # Setup test data with nested structures and None values
        class Product(Prodict):
            name: str
            price: int
            category: str

        class Store(Prodict):
            name: str
            product: Product
            products: List[Product]
            location: str

        # Create test objects
        product_with_price = Product(name='Laptop', price=1000, category='Electronics')
        product_without_price = Product(name='Mouse', price=None, category='Electronics')
        product_partial = Product(name='Keyboard', price=50, category=None)

        store = Store(
            name='TechStore',
            product=product_with_price,
            products=[product_without_price, product_partial],
            location=None
        )

        # Test 1: Default behavior (all False)
        # Expected: Top-level dict, nested Prodict remains, None values included, list items as Prodict
        result1 = store.to_dict(is_recursive=False, exclude_none=False, exclude_none_in_lists=False)
        assert isinstance(result1, dict)
        assert isinstance(result1['product'], Product), "Nested Prodict should remain as Prodict"
        assert isinstance(result1['products'][0], Product), "List items should remain as Prodict"
        assert 'location' in result1, "None values should be included"
        assert result1['location'] is None

        # Test 2: is_recursive=True only
        # Expected: Direct nested Prodict converted to dict, list items remain as Prodict
        # Note: is_recursive only converts nested Prodict attributes, NOT items inside lists
        result2 = store.to_dict(is_recursive=True, exclude_none=False, exclude_none_in_lists=False)
        assert isinstance(result2, dict)
        assert isinstance(result2['product'], dict), "is_recursive should convert nested Prodict to dict"
        assert not isinstance(result2['product'], Prodict)
        assert isinstance(result2['products'][0], Product), "List items remain as Prodict without convert_list_items"

        # Test 3: exclude_none=True only
        # Expected: Top-level None values excluded, nested Prodict remains, list items as Prodict
        result3 = store.to_dict(is_recursive=False, exclude_none=True, exclude_none_in_lists=False)
        assert isinstance(result3, dict)
        assert 'location' not in result3, "exclude_none should exclude None values from result"
        assert isinstance(result3['product'], Product), "Nested Prodict should remain"
        assert isinstance(result3['products'][0], Product), "List items should remain as Prodict"

        # Test 4: exclude_none_in_lists=True only (implies convert_list_items=True)
        # Expected: Nested Prodict remains, list items converted to dict WITHOUT None values
        result4 = store.to_dict(is_recursive=False, exclude_none=False, exclude_none_in_lists=True)
        assert isinstance(result4, dict)
        assert isinstance(result4['product'], Product), "Nested Prodict should remain"
        assert isinstance(result4['products'][0], dict), "exclude_none_in_lists converts list items to dict"
        assert 'price' not in result4['products'][0], "None values in list items should be excluded"
        assert 'name' in result4['products'][0], "Non-None values should be present"
        assert 'category' not in result4['products'][1], "None category should be excluded"

        # Test 5: is_recursive=True, exclude_none=True
        # Expected: Direct nested Prodict to dict, top-level None excluded, list items remain as Prodict
        result5 = store.to_dict(is_recursive=True, exclude_none=True, exclude_none_in_lists=False)
        assert isinstance(result5, dict)
        assert 'location' not in result5, "Top-level None should be excluded"
        assert isinstance(result5['product'], dict), "Nested Prodict should be dict"
        assert isinstance(result5['products'][0], Product), "List items remain as Prodict without convert_list_items"

        # Test 6: is_recursive=True, exclude_none_in_lists=True
        # Expected: All Prodict to dict, top-level None kept, list items without None
        result6 = store.to_dict(is_recursive=True, exclude_none=False, exclude_none_in_lists=True)
        assert isinstance(result6, dict)
        assert 'location' in result6, "Top-level None should be kept"
        assert isinstance(result6['product'], dict), "Nested Prodict should be dict"
        assert isinstance(result6['products'][0], dict), "List items should be dict"
        assert 'price' not in result6['products'][0], "None in list items should be excluded"

        # Test 7: exclude_none=True, exclude_none_in_lists=True
        # Expected: Top-level None excluded, nested Prodict remains, list items as dict without None
        result7 = store.to_dict(is_recursive=False, exclude_none=True, exclude_none_in_lists=True)
        assert isinstance(result7, dict)
        assert 'location' not in result7, "Top-level None should be excluded"
        assert isinstance(result7['product'], Product), "Nested Prodict should remain"
        assert isinstance(result7['products'][0], dict), "List items should be dict"
        assert 'price' not in result7['products'][0], "None in list items should be excluded"

        # Test 8: All True
        # Expected: All Prodict to dict, all None excluded everywhere
        result8 = store.to_dict(is_recursive=True, exclude_none=True, exclude_none_in_lists=True)
        assert isinstance(result8, dict)
        assert 'location' not in result8, "Top-level None should be excluded"
        assert isinstance(result8['product'], dict), "Nested Prodict should be dict"
        assert isinstance(result8['products'][0], dict), "List items should be dict"
        assert 'price' not in result8['products'][0], "None in list items should be excluded"
        assert 'category' not in result8['products'][1], "None in list items should be excluded"

    def test_convert_list_items_parameter(self):
        """
        Test the new convert_list_items parameter that allows converting list items
        to dict while keeping None values (unlike exclude_none_in_lists which always excludes None)
        """
        class Item(Prodict):
            name: str
            value: int
            code: str

        class Container(Prodict):
            title: str
            items_list: List[Item]

        item1 = Item(name='A', value=10, code=None)
        item2 = Item(name='B', value=None, code='B01')
        item3 = Item(name='C', value=30, code='C01')

        container = Container(title='TestContainer', items_list=[item1, item2, item3])

        # Test 1: convert_list_items=False (default) - list items stay as Prodict
        result1 = container.to_dict(convert_list_items=False)
        assert isinstance(result1['items_list'][0], Item), "List items should remain as Prodict"
        assert isinstance(result1['items_list'][1], Item)

        # Test 2: convert_list_items=True, exclude_none=False - convert to dict, keep None
        result2 = container.to_dict(convert_list_items=True, exclude_none=False)
        assert isinstance(result2['items_list'][0], dict), "List items should be converted to dict"
        assert not isinstance(result2['items_list'][0], Prodict)
        assert 'code' in result2['items_list'][0], "None values should be kept"
        assert result2['items_list'][0]['code'] is None
        assert 'value' in result2['items_list'][1], "None values should be kept"
        assert result2['items_list'][1]['value'] is None

        # Test 3: convert_list_items=True, exclude_none=True - convert to dict, exclude None
        result3 = container.to_dict(convert_list_items=True, exclude_none=True)
        assert isinstance(result3['items_list'][0], dict)
        assert 'code' not in result3['items_list'][0], "None values should be excluded from list items"
        assert 'name' in result3['items_list'][0], "Non-None values should be present"
        assert 'value' not in result3['items_list'][1], "None values should be excluded"

        # Test 4: convert_list_items=True, is_recursive=True - everything becomes dict
        result4 = container.to_dict(convert_list_items=True, is_recursive=True)
        assert isinstance(result4, dict)
        assert isinstance(result4['items_list'][0], dict)
        assert 'code' in result4['items_list'][0], "None should be kept with exclude_none=False"

        # Test 5: Verify backward compatibility - exclude_none_in_lists still works
        result5 = container.to_dict(exclude_none_in_lists=True)
        assert isinstance(result5['items_list'][0], dict), "exclude_none_in_lists should convert to dict"
        assert 'code' not in result5['items_list'][0], "exclude_none_in_lists should exclude None"

        # Test 6: convert_list_items with nested structures
        class Nested(Prodict):
            container: Container
            count: int

        nested = Nested(container=container, count=5)

        result6 = nested.to_dict(is_recursive=True, convert_list_items=True, exclude_none=False)
        assert isinstance(result6['container'], dict), "Nested Prodict should be dict"
        assert isinstance(result6['container']['items_list'][0], dict), "List items should be dict"
        assert 'code' in result6['container']['items_list'][0], "None should be kept"

        # Test 7: Demonstrate the key difference between convert_list_items and exclude_none_in_lists
        result_with_convert = container.to_dict(convert_list_items=True, exclude_none=False)
        result_with_exclude = container.to_dict(exclude_none_in_lists=True)

        # Both convert to dict
        assert isinstance(result_with_convert['items_list'][0], dict)
        assert isinstance(result_with_exclude['items_list'][0], dict)

        # But convert_list_items keeps None, exclude_none_in_lists removes it
        assert 'code' in result_with_convert['items_list'][0]
        assert result_with_convert['items_list'][0]['code'] is None
        assert 'code' not in result_with_exclude['items_list'][0]

    def test_dict_value_edge_cases(self):
        """
        Test _dict_value with edge cases like None values, empty lists, nested lists
        """
        from prodict import _dict_value

        class Thing(Prodict):
            label: str
            amount: int

        # Test None value
        assert _dict_value(None, False, False, False, False) is None
        assert _dict_value(None, True, True, True, True) is None

        # Test empty list
        empty_list = []
        assert _dict_value(empty_list, False, False, False, False) == []
        assert _dict_value(empty_list, True, True, True, True) == []

        # Test list with None values (not Prodict)
        list_with_none = [1, None, 3]
        result = _dict_value(list_with_none, False, False, True, False)
        assert result == [1, None, 3], "exclude_none_in_lists only affects Prodict items"

        # Test list with mixed Prodict and non-Prodict
        thing1 = Thing(label='test', amount=None)
        mixed_list = [thing1, 'plain_string', 42]
        result = _dict_value(mixed_list, False, False, True, False)
        assert isinstance(result, list)
        assert isinstance(result[0], dict), "Prodict in list converts to dict"
        assert 'amount' not in result[0], "None excluded from Prodict in list"
        assert result[1] == 'plain_string'
        assert result[2] == 42

        # Test deeply nested Prodict
        class Wrapper(Prodict):
            thing: Thing
            depth: int

        wrapped = Wrapper(thing=Thing(label='nested', amount=100), depth=2)

        # Non-recursive keeps it as Prodict
        result_non_recursive = _dict_value(wrapped, False, False, False, False)
        assert isinstance(result_non_recursive, Wrapper)

        # Recursive converts to dict, nested Thing also converts
        result_recursive = _dict_value(wrapped, True, False, False, False)
        assert isinstance(result_recursive, dict)
        assert 'thing' in result_recursive
        # The nested thing gets converted via to_dict
        assert isinstance(result_recursive['thing'], dict)

    def test_positional_dict_keeps_annotated_values(self):
        # #55: a positional dict must not lose the values of annotated attributes
        class Model(Prodict):
            n: int
            child: Ram

        m = Model({'n': '7', 'child': {'capacity': '8'}, 'extra': 1})
        self.assertEqual(m, {'n': 7, 'child': {'brand': None, 'capacity': 8, 'unit': None},
                             'extra': 1})
        self.assertIsInstance(m.child, Ram)
        self.assertEqual(Model({'n': '7'}), Model.from_dict({'n': '7'}))

        # an iterable of pairs works the same way, and is only consumed once
        self.assertEqual(Model(iter([('n', '3')])).n, 3)

        # keyword arguments still win over the positional dict
        self.assertEqual(Model({'n': '1'}, n='2').n, 2)

        # positional values also win over init() defaults, like keyword arguments
        class WithDefault(Prodict):
            n: int

            def init(self):
                self.n = 5

        self.assertEqual(WithDefault().n, 5)
        self.assertEqual(WithDefault({'n': '6'}).n, 6)
        self.assertIsNone(WithDefault({'n': None}).n)

    def test_prodict_value_for_dict_bool_tuple_annotations(self):
        # #56: a Prodict assigned to a dict, bool or tuple attribute is stored
        class M(Prodict):
            d: dict
            ok: bool
            pair: tuple
            nums: List[int]

        inner = Prodict(a=1)
        m = M(d=inner, ok=Prodict(a=1), pair=Prodict(a=1), nums=Prodict(a=1))
        self.assertIs(m.d, inner)
        self.assertEqual(m.ok, {'a': 1})
        self.assertEqual(m.pair, {'a': 1})
        self.assertEqual(m.nums, {'a': 1})

        # a plain dict for a dict attribute still becomes a Prodict
        self.assertIsInstance(M(d={'a': 1}).d, Prodict)

        # deepcopy copies every value, including the Prodict in d
        m2 = M(d={'a': {'b': 2}})
        clone = copy.deepcopy(m2)
        self.assertEqual(clone, m2)
        self.assertIsInstance(clone, M)
        self.assertIsInstance(clone.d, Prodict)
        self.assertIsNot(clone.d, m2.d)

        # a Prodict subclass value keeps its class in a dict attribute
        ram = Ram(capacity=4)
        self.assertIs(M(d=ram).d, ram)

    def test_typing_dict_annotation(self):
        # #57: Dict[K, V] and bare Dict accept dict values like dict does
        class M(Prodict):
            d: Dict[str, int]
            bare: Dict

        m = M(d={'a': 1}, bare={'b': {'c': 2}})
        self.assertEqual(m, {'d': {'a': 1}, 'bare': {'b': {'c': 2}}})
        self.assertIsInstance(m.d, Prodict)
        self.assertEqual(m.d.a, 1)
        self.assertIsInstance(m.bare, Prodict)
        self.assertEqual(M(), {'d': None, 'bare': None})
        self.assertEqual(copy.deepcopy(m), m)

        m.d = Prodict(x=1)
        self.assertEqual(m.d, {'x': 1})

    def test_optional_and_union_annotations(self):
        # #38: Optional[X] converts as X; a union of several types stores the value as given
        class M(Prodict):
            n: Optional[int]
            child: Optional[Ram]
            either: Union[int, str]
            maybe_either: Optional[Union[int, str]]
            nums: List[Optional[int]]

        m = M(n='7', child={'capacity': '8'}, either='7', maybe_either='7', nums=['1', None])
        self.assertEqual(m.n, 7)
        self.assertIsInstance(m.child, Ram)
        self.assertEqual(m.child.capacity, 8)
        self.assertEqual(m.either, '7')
        self.assertEqual(m.maybe_either, '7')
        self.assertEqual(m.nums, [1, None])
        self.assertIs(type(M(either=7).either), int)
        data = {'a': 1}
        self.assertIs(M(either=data).either, data)
        self.assertIsNone(M(n=None).n)

    @unittest.skipIf(sys.version_info < (3, 10), 'X | Y annotations need Python 3.10')
    def test_union_operator_annotations(self):
        module = make_module('prodict_test_union_operator', (
            'from prodict import Prodict\n'
            'class M(Prodict):\n'
            '    n: int | None\n'
            '    either: int | str\n'))
        self.assertEqual(module.M(n='7').n, 7)
        self.assertEqual(module.M(either='7').either, '7')
        self.assertIs(type(module.M(either=7).either), int)
        data = {'a': 1}
        self.assertIs(module.M(either=data).either, data)

    @unittest.skipIf(sys.version_info < (3, 9), 'built-in generics need Python 3.9')
    def test_builtin_generic_annotations(self):
        # #21: list[T], tuple[...] and dict[K, V] work like their typing forms
        module = make_module('prodict_test_builtin_generics', (
            'from typing import Annotated\n'
            'from prodict import Prodict\n'
            'from test_prodict import Ram\n'
            'class M(Prodict):\n'
            '    nums: list[int]\n'
            '    pair: tuple[int, ...]\n'
            '    d: dict[str, int]\n'
            '    rams: list[Ram]\n'
            '    meta: Annotated[int, "unit: seconds"]\n'))
        m = module.M(nums=['1', '2'], pair=[1, 2], d={'a': 1}, rams=[{'capacity': '4'}], meta='7')
        self.assertEqual(m.nums, [1, 2])
        self.assertEqual(m.pair, (1, 2))
        self.assertIsInstance(m.d, Prodict)
        self.assertIsInstance(m.rams[0], Ram)
        self.assertEqual(m.rams[0].capacity, 4)
        self.assertEqual(m.meta, 7)
        self.assertEqual(module.M(nums=5).nums, 5)

    def test_failed_conversion_stores_value_as_given(self):
        class M(Prodict):
            n: int
            f: float
            nums: List[int]
            seq: list
            pair: Tuple[int, int]

        m = M(n='many', f='x', nums=['1', 'two'], seq=5, pair=5)
        self.assertEqual(m, {'n': 'many', 'f': 'x', 'nums': [1, 'two'], 'seq': 5, 'pair': 5})
        m.n = '3'
        self.assertEqual(m.n, 3)
        self.assertEqual(M(n=Prodict(a=1)).n, {'a': 1})
        self.assertEqual(M(n=float('inf')).n, float('inf'))  # OverflowError

    def test_list_items(self):
        # List[T] passes each item through T, as before; List[Any] keeps items as they are
        class M(Prodict):
            anything: List[Any]
            pairs: List[tuple]
            flags: List[bool]
            amounts: List[Decimal]
            dicts: List[dict]

        data, ram = {'a': 1}, Ram(capacity=1)
        m = M(anything=[data, ram, '1', None], pairs=[[1, 2]], flags=[0, 1],
              amounts=['1.5'], dicts=[{'a': 1}])
        self.assertIs(m.anything[0], data)
        self.assertIs(m.anything[1], ram)
        self.assertEqual(m.anything[2:], ['1', None])
        self.assertEqual(m.pairs, [(1, 2)])
        self.assertIs(m.flags[0], False)
        self.assertIs(m.flags[1], True)
        self.assertEqual(m.amounts, [Decimal('1.5')])
        self.assertIsInstance(m.dicts[0], Prodict)

    def test_dicts_with_any_keys_become_prodicts(self):
        # keys named like dict methods, and keys that are not strings, are fine
        class M(Prodict):
            d: dict
            rows: List[dict]

        m = M(d={'items': [1]}, rows=[{'items': 1}, {1: 'one'}, {'a': 1}])
        self.assertIsInstance(m.d, Prodict)
        self.assertEqual(m.d['items'], [1])
        self.assertTrue(all(type(row) is Prodict for row in m.rows))
        self.assertEqual(m.rows[1][1], 'one')

    def test_list_items_that_cannot_be_converted(self):
        class TD(TypedDict):
            a: int

        class M(Prodict):
            amounts: List[Decimal]
            maybe_amounts: List[Optional[Decimal]]
            typed: List[TD]

        item = {'a': 1}
        m = M(amounts=['1.5', 'bad'], maybe_amounts=['2.5', None], typed=[item])
        self.assertEqual(m.amounts, [Decimal('1.5'), 'bad'])
        self.assertEqual(m.maybe_amounts, [Decimal('2.5'), None])
        self.assertIsInstance(m.maybe_amounts[0], Decimal)
        self.assertIs(m.typed[0], item)

    @unittest.skipIf(sys.version_info < (3, 9), 'Annotated needs Python 3.9')
    def test_annotated_is_converted_as_its_type(self):
        from typing import Annotated
        # get_type_hints() strips Annotated; _convert handles it when it does not
        self.assertEqual(prodict._convert(Annotated[int, 'meta'], '7'), 7)
        self.assertEqual(prodict._convert_item(Annotated[Decimal, 'meta'], '1.5'), Decimal('1.5'))

    def test_annotations_are_inherited(self):
        class Base(Prodict):
            id: int

        class Child(Base):
            name: str

        class Empty(Base):
            pass

        class Override(Base):
            id: str

        class Other(Prodict):
            size: float

        class Both(Child, Other):
            pass

        self.assertEqual(Child(id='1', name=2), {'id': 1, 'name': '2'})
        self.assertEqual(Child(), {'id': None, 'name': None})
        self.assertEqual(Child.attr_names(), ['id', 'name'])
        self.assertEqual(Empty(id='1').id, 1)
        self.assertEqual(Override(id=1).id, '1')
        self.assertEqual(Both(id='1', name=2, size='3'), {'id': 1, 'name': '2', 'size': 3.0})

    def test_string_annotations(self):
        node = ForwardNode(value='1', children=[{'value': '2', 'children': []}])
        self.assertEqual(node.value, 1)
        self.assertIsInstance(node.children[0], ForwardNode)
        self.assertEqual(node.children[0].value, 2)

        # an annotation that cannot be resolved stores values as given; the others still convert
        data = {'a': 1}
        ref = UnresolvedRef(later=data, n='2')
        self.assertIs(ref.later, data)
        self.assertEqual(ref.n, 2)

    def test_future_annotations(self):
        module = make_module('prodict_test_future', (
            'from typing import ClassVar, List, Optional\n'
            'from prodict import Prodict\n'
            'class Node(Prodict):\n'
            '    VERSION: ClassVar[int] = 1\n'
            '    value: int\n'
            '    children: List[Node]\n'
            '    parent: Optional[Node]\n'
            '    other: Missing\n'
            'class Leaf(Node):\n'
            '    label: str\n'), future_annotations=True)
        node = module.Node(value='1', children=[{'value': '2'}], parent={'value': '0'}, other={'a': 1})
        self.assertEqual(node.value, 1)
        self.assertIsInstance(node.children[0], module.Node)
        self.assertIsInstance(node.parent, module.Node)
        self.assertIs(type(node.other), dict)
        self.assertNotIn('VERSION', node)
        self.assertEqual(module.Leaf(value='3', label=4), {'value': 3, 'children': None, 'parent': None,
                                                          'other': None, 'label': '4'})

    def test_forward_reference_defined_later(self):
        module = make_module('prodict_test_forward', (
            'from prodict import Prodict\n'
            'class Owner(Prodict):\n'
            '    pet: Pet\n'
            '    age: int\n'), future_annotations=True)
        self.assertIs(type(module.Owner(pet={'name': 'Rex'}, age='3').pet), dict)
        exec('class Pet(Prodict):\n    name: str\n', module.__dict__)
        owner = module.Owner(pet={'name': 'Rex'}, age='3')
        self.assertIsInstance(owner.pet, module.Pet)
        self.assertEqual(owner.age, 3)

    def test_forward_reference_named_like_class_var(self):
        module = make_module('prodict_test_class_var_name', (
            'from prodict import Prodict\n'
            'class Holder(Prodict):\n'
            '    variant: ClassVariant\n'), future_annotations=True)
        self.assertEqual(module.Holder.attr_names(), ['variant'])
        exec('class ClassVariant(Prodict):\n    code: int\n', module.__dict__)
        self.assertIsInstance(module.Holder(variant={'code': '1'}).variant, module.ClassVariant)
        self.assertIs(module.Holder.attr_types()['variant'], module.ClassVariant)

    def test_qualified_name_ending_in_class_var_is_a_field(self):
        module = make_module('prodict_test_qualified_class_var', (
            'import types\n'
            'from prodict import Prodict\n'
            'models = types.SimpleNamespace()\n'
            'class Holder(Prodict):\n'
            '    child: models.ClassVar\n'), future_annotations=True)
        self.assertEqual(module.Holder.attr_names(), ['child'])
        exec('class Child(Prodict):\n    pass\nmodels.ClassVar = Child\n', module.__dict__)
        self.assertIsInstance(module.Holder(child={}).child, module.Child)

    def test_internal_names_do_not_hide_keys(self):
        p = Prodict(_prodict_attr_types=7)
        p.attr_types()
        self.assertEqual(p._prodict_attr_types, 7)

    def test_list_item_isinstance_failure(self):
        class Strict(type):
            def __instancecheck__(cls, item):
                raise ValueError('no isinstance() here')

        class Target(metaclass=Strict):
            def __init__(self, item):
                self.item = item

        class M(Prodict):
            targets: List[Target]

        self.assertEqual(M(targets=['x']).targets, ['x'])

    def test_aliased_class_var(self):
        module = make_module('prodict_test_aliased_class_var', (
            'import typing as t\n'
            'from prodict import Prodict\n'
            'class M(Prodict):\n'
            '    registry: t.ClassVar[t.Dict[str, Later]] = {}\n'
            '    bare: t.ClassVar = 1\n'
            '    n: int\n'), future_annotations=True)
        self.assertEqual(module.M.attr_names(), ['n'])
        self.assertEqual(module.M(n='2'), {'n': 2})

    def test_class_var_lookup_that_raises(self):
        module = make_module('prodict_test_lazy_lookup', (
            'from prodict import Prodict\n'
            'class Lazy:\n'
            '    def __getattr__(self, name):\n'
            '        raise RuntimeError("not loaded")\n'
            'lazy = Lazy()\n'
            'class M(Prodict):\n'
            '    x: lazy.ClassVar\n'
            '    n: int\n'), future_annotations=True)
        self.assertEqual(module.M(x='raw', n='2'), {'x': 'raw', 'n': 2})

    def test_assignment_uses_one_annotation_snapshot(self):
        class M(Prodict):
            n: int

        m = M()
        # another thread may change the annotations between two lookups
        with mock.patch.object(M, 'attr_types', side_effect=[{'n': int}, {}]):
            m.set_attribute('n', '1')
        self.assertEqual(m.n, 1)

    def test_resolution_order_of_names(self):
        # a class attribute named like a class: the annotation means the class
        # in the module, whether or not another annotation fails to resolve
        module = make_module('prodict_test_names', (
            'from prodict import Prodict\n'
            'class Pet(Prodict):\n'
            '    name: str\n'
            'class Owner(Prodict):\n'
            '    Pet: Pet = None\n'
            'class BrokenOwner(Prodict):\n'
            '    Pet: Pet = None\n'
            '    other: Missing\n'), future_annotations=True)
        self.assertIs(module.Owner.attr_types()['Pet'], module.Pet)
        self.assertIs(module.BrokenOwner.attr_types()['Pet'], module.Pet)

    def test_forward_reference_from_threads(self):
        module = make_module('prodict_test_threads', (
            'from prodict import Prodict\n'
            'class Owner(Prodict):\n'
            '    pet: Pet\n'), future_annotations=True)
        module.Owner()
        exec('class Pet(Prodict):\n    name: str\n', module.__dict__)
        barrier, results, errors = threading.Barrier(8), [], []

        def work():
            barrier.wait()
            try:
                results.append(type(module.Owner(pet={'name': 'Rex'}).pet))
            except Exception as error:  # pragma: no cover
                errors.append(error)

        threads = [threading.Thread(target=work) for _ in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(errors, [])
        self.assertEqual(results, [module.Pet] * 8)

    def test_models_can_be_garbage_collected(self):
        def make():
            class Node(Prodict):
                parent: 'Node'
                value: int

            Node(value='1', parent={'value': '2'})
            return weakref.ref(Node)

        ref = make()
        gc.collect()
        self.assertIsNone(ref())

    @unittest.skipIf(sys.version_info < (3, 14), 'lazy annotations need Python 3.14')
    def test_lazy_annotations(self):
        module = make_module('prodict_test_lazy', (
            'from prodict import Prodict\n'
            'class M(Prodict):\n'
            '    other: NoSuchName\n'
            '    n: int\n'))
        data = {'a': 1}
        m = module.M(other=data, n='2')
        self.assertIs(m.other, data)
        self.assertEqual(m.n, 2)

    def test_class_var_annotations_are_not_keys(self):
        from typing import ClassVar

        class Base(Prodict):
            VERSION: ClassVar[int] = 1
            id: int

        class Child(Base):
            name: str

        self.assertEqual(Child(id='2'), {'id': 2, 'name': None})
        self.assertEqual(Child().VERSION, 1)
        self.assertEqual(Base.attr_names(), ['id'])

    def test_prodict_values_keep_identity(self):
        class M(Prodict):
            child: Ram
            any_model: Prodict
            rams: List[Ram]

        ram = Ram(capacity=4)
        m = M(child=ram, any_model=ram, rams=[ram])
        self.assertIs(m.child, ram)
        self.assertIs(m.any_model, ram)
        self.assertIs(m.rams[0], ram)

    def test_any_key_is_accepted_as_data(self):
        # keys named like dict methods, and keys that are not strings, work as in a dict
        page = Prodict.from_dict({'items': [1, 2], 'total': 2, 'meta': {'keys': 'a'}})
        self.assertEqual(page['items'], [1, 2])
        self.assertEqual(page.total, 2)
        self.assertIsInstance(page.meta, Prodict)
        self.assertEqual(page.meta['keys'], 'a')
        self.assertTrue(callable(page.items))
        self.assertEqual(Prodict(items=1)['items'], 1)
        self.assertEqual(Prodict.from_dict({1: 'one'})[1], 'one')
        with self.assertRaises(TypeError):
            page.items = 1  # still not as an attribute

    def test_positional_dict_is_like_from_dict(self):
        # #42: nested dicts passed positionally become Prodicts too
        data = {'x': 100, 'foo': {'z': 300, 'deeper': {'w': 1}}}
        p = Prodict(data)
        self.assertEqual(p.foo.z, 300)
        self.assertEqual(p.foo.deeper.w, 1)
        self.assertIs(type(p.foo), Prodict)
        self.assertEqual(p, Prodict.from_dict(data))
        self.assertEqual(Prodict([('foo', {'z': 1})]).foo.z, 1)

    def test_prodict_values_are_not_copied(self):
        other = Prodict(x=1)
        p = Prodict(a=other)
        p.b = other
        self.assertIs(p.a, other)
        self.assertIs(p.b, other)
        self.assertIs(Prodict({'c': other}).c, other)

    def clones(self, value):
        # every way to copy a Prodict: copy, deepcopy and pickle with each protocol
        yield copy.copy(value)
        yield copy.deepcopy(value)
        for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
            yield pickle.loads(pickle.dumps(value, protocol))

    def test_copy_deepcopy_and_pickle_keep_data_as_stored(self):
        c = Counter(n='1')
        c['n'] = '2'        # raw, would convert to 2
        del c['log']        # init() would put it back
        c['items'] = [1]
        c[3] = 'three'
        calls = len(Counter.init_calls)
        for clone in self.clones(c):
            self.assertIs(type(clone), Counter)
            self.assertEqual(clone, {'n': '2', 'items': [1], 3: 'three'})
        self.assertEqual(len(Counter.init_calls), calls)
        self.assertIs(copy.copy(c)['items'], c['items'])
        self.assertIsNot(copy.deepcopy(c)['items'], c['items'])

    def test_copies_keep_instance_attributes_and_slots(self):
        p = Prodict(a=1)
        vars(p)['note'] = 'kept'
        s = Slotted(a=1)
        object.__setattr__(s, 'tag', 'x')
        object.__setattr__(s, '_Slotted__secret', 'y')
        for clone in self.clones(p):
            self.assertEqual(vars(clone), {'note': 'kept'})
            self.assertEqual(clone, {'a': 1})
        for clone in self.clones(s):
            self.assertEqual((clone.tag, clone._Slotted__secret), ('x', 'y'))
            self.assertEqual(clone, {'a': 1})

    def test_deepcopy_and_pickle_of_shared_and_cyclic_values(self):
        shared = Prodict(v=1)
        p = Prodict(a=shared, b=shared)
        p['me'] = p
        shallow, *deep = self.clones(p)
        self.assertIs(shallow['me'], p)  # a shallow copy points at the original, as a dict's does
        for clone in deep:
            self.assertIs(clone.a, clone.b)
            self.assertIs(clone['me'], clone)

    def test_cyclic_and_shared_dicts_in_data(self):
        d = {'name': 'loop'}
        d['me'] = d
        for p in (Prodict(d), Prodict.from_dict(d), Prodict(wrapper=d).wrapper):
            self.assertIs(p.me, p)
            self.assertEqual(p.name, 'loop')
        shared = {'v': 1}
        both = Prodict(a=shared, b=shared)
        self.assertEqual(both.a, both.b)  # converted once per occurrence, as before

    def test_from_dict_with_a_custom_constructor(self):
        self.assertEqual(Strict.from_dict({'x': 1}), {'x': 1})

        class Holder(Prodict):
            child: Strict

        self.assertIsInstance(Holder(child={'x': 1}).child, Strict)

    def test_class_attributes_named_like_dict_methods(self):
        M = type('M', (Prodict,), {'__annotations__': {'items': list}, 'items': None})
        m = M()
        self.assertEqual(dict(m), {'items': None})
        self.assertEqual(m.to_dict(), {'items': None})
        self.assertIn('to_dict', dir(m))

    def test_delete_instance_attributes(self):
        class Cached(Prodict):
            @functools.cached_property
            def total(self):
                return 3

        c = Cached(a=1)
        self.assertEqual(c.total, 3)
        del c.total  # a cached value, not a key
        self.assertEqual(c, {'a': 1})

    def test_keys_named_like_special_methods(self):
        hooks = {'__deepcopy__': 1, '__getstate__': 2, '__reduce_ex__': 3, '__copy__': 4}
        p = Prodict(nested={'__deepcopy__': 5}, **hooks)
        for clone in self.clones(p):
            self.assertEqual(clone, p)
        self.assertEqual(p['__deepcopy__'], 1)
        with self.assertRaises(AttributeError):
            p.__deepcopy__  # a special-method name is never a key lookup

    def test_pickles_from_0_8_load(self):
        # Prodict(a=1, b={'c': 2}) pickled by prodict 0.8.23 (protocol 2)
        old = (b'\x80\x02cprodict\nProdict\nq\x00)\x81q\x01(X\x01\x00\x00\x00aq\x02K\x01X\x01\x00\x00\x00b'
               b'q\x03h\x00)\x81q\x04X\x01\x00\x00\x00cq\x05K\x02s}q\x06h\x05K\x02sbu}q\x07(h\x02K\x01h\x03h\x04ub.')
        p = pickle.loads(old)
        self.assertEqual(p, {'a': 1, 'b': {'c': 2}})
        self.assertIsInstance(p.b, Prodict)
        self.assertEqual(vars(p), {})

    def test_delete_attribute(self):
        p = Prodict(a=1, b=2)
        del p.a
        self.assertEqual(p, {'b': 2})
        with self.assertRaises(AttributeError):
            del p.a
        with self.assertRaises(TypeError):
            del p.items

    def test_dir_lists_keys(self):
        p = Prodict({'alpha': 1, 'not-an-identifier': 2, 3: 'three'})
        names = dir(p)
        self.assertIn('alpha', names)
        self.assertIn('to_dict', names)
        self.assertNotIn('not-an-identifier', names)

    def test_from_dict_with_other_constructors(self):
        self.assertEqual(Positional.from_dict({'x': 1}), {'x': 1})
        self.assertEqual(Positional.from_dict({'x': 1, 1: 'one'}), {'x': 1, 1: 'one'})
        d = {'name': 'loop'}
        d['me'] = d
        strict = Strict.from_dict(d)
        # 'me' is not annotated, so it becomes a Prodict, which contains itself
        self.assertIs(type(strict['me']), Prodict)
        self.assertIs(strict['me']['me'], strict['me'])
        shared = {'x': 1}

        class Holder(Prodict):
            a: Strict
            b: Strict

        holder = Holder(a=shared, b=shared)
        # a custom constructor gets its own instance for each occurrence
        self.assertIsInstance(holder.a, Strict)
        self.assertEqual(holder.a, holder.b)

    def test_from_dict_binds_named_parameters(self):
        class Named(Prodict):
            def __init__(self, name):
                super().__init__(name=name)

        class KeywordOnly(Prodict):
            def __init__(self, *, name):
                super().__init__(name=name)

        class Defaults(Prodict):
            def __init__(self, a=0, b=0):
                super().__init__(a=a, b=b)

        self.assertEqual(Named.from_dict({'name': 'Ada'}), {'name': 'Ada'})
        self.assertEqual(KeywordOnly.from_dict({'name': 'Ada'}), {'name': 'Ada'})
        self.assertEqual(Defaults.from_dict({'a': 1, 'b': 2}), {'a': 1, 'b': 2})

    def test_from_dict_with_annotations_that_do_not_resolve(self):
        module = make_module('prodict_test_ctor_annotations', (
            'from prodict import Prodict\n'
            'class C(Prodict):\n'
            '    def __init__(self, **kw: Missing):\n'
            '        super().__init__(**kw)\n'), future_annotations=sys.version_info < (3, 14))
        self.assertEqual(module.C.from_dict({'a': 1}), {'a': 1})

    def test_model_failing_after_base_init_is_not_reused(self):
        class Late(Prodict):
            x: int

            def __init__(self, data):
                super().__init__(data)
                raise ValueError('rejected after construction')

        class Holder(Prodict):
            a: Late
            b: Late

        d = {'x': '1'}
        holder = Holder(a=d, b=d)
        self.assertIs(holder.a, d)
        self.assertIs(holder.b, d)

    def test_init_assigning_one_dict_twice(self):
        settings = {'level': 1}

        class Item(Prodict):
            def init(self):
                self.first = settings
                self.second = settings

        item = Item()
        self.assertIsNot(item.first, item.second)

    def test_self_reference_in_a_model_is_the_model(self):
        class Node(Prodict):
            name: str

        d = {'name': 'root'}
        d['me'] = d
        node = Node(d)
        self.assertIs(node.me, node)

    def test_failed_nested_model_is_not_reused(self):
        class Broken(Prodict):
            x: int

            def init(self):
                raise ValueError('cannot build')

        class Holder(Prodict):
            a: Broken
            b: Broken

        d = {'x': '1'}
        holder = Holder(a=d, b=d)
        self.assertIs(holder.a, d)
        self.assertIs(holder.b, d)

    def test_positional_and_keyword_data_together(self):
        d = {'x': 1}
        p = Prodict(d, z=d)
        self.assertIsNot(p.z, p)
        self.assertEqual(p.z, {'x': 1})

    def test_init_defaults_are_not_shared(self):
        defaults = {'level': 1}

        class Item(Prodict):
            def init(self):
                self.meta = defaults

        class Pair(Prodict):
            a: Item
            b: Item

        pair = Pair(a={}, b={})
        self.assertIsNot(pair.a.meta, pair.b.meta)

    def test_copies_honor_subclass_hooks(self):
        point = Point(1, 2)
        session = Session(user='ada')
        vars(session)['token'] = 'secret'
        for clone in self.clones(point):
            self.assertEqual(clone, {'x': 1, 'y': 2})
            self.assertIs(type(clone), Point)
        for clone in self.clones(session):
            self.assertEqual(clone, {'user': 'ada'})
            self.assertIsNone(vars(clone)['token'])

    def test_private_slot_on_an_underscore_class(self):
        cls = type('_', (Prodict,), {'__slots__': '__s'})
        p = cls()
        object.__setattr__(p, '__s', 7)
        self.assertEqual(getattr(copy.copy(p), '__s'), 7)

    def test_delete_prefers_instance_attributes(self):
        class Cached(Prodict):
            @functools.cached_property
            def total(self):
                return 3

        c = Cached({'total': 99})
        self.assertEqual(c.total, 3)  # the cached property wins on reads
        del c.total
        self.assertEqual(c['total'], 99)

    def test_delete_a_key_named_like_an_empty_slot(self):
        s = Slotted(tag=1)
        del s.tag
        self.assertNotIn('tag', s)

    @unittest.skipIf(sys.version_info < (3, 11), 'object.__getstate__ needs Python 3.11')
    def test_subclass_state_from_object_getstate(self):
        cls = type('SlottedState', (Slotted,), {'__getstate__': lambda self: object.__getstate__(self)})
        s = cls(a=1)
        object.__setattr__(s, 'tag', 'x')
        clone = copy.copy(s)
        self.assertEqual((clone.tag, clone), ('x', {'a': 1}))

    def test_dunder_rule(self):
        p = Prodict({'__': 1, '__x__': 2})
        self.assertEqual(p.__, 1)  # too short to be a special name
        self.assertNotIn('__x__', dir(p))
        with self.assertRaises(AttributeError):
            del p.__x__
        self.assertEqual(p['__x__'], 2)

    def test_one_dict_as_several_models(self):
        class A(Prodict):
            x: int

        class B(Prodict):
            x: str

        class H(Prodict):
            a: A
            b: B
            raw: dict

        d = {'x': '1'}
        h = H(a=d, b=d, raw=d)
        self.assertEqual((h.a.x, h.b.x), (1, '1'))
        self.assertIs(type(h.raw), Prodict)

    def test_cycle_through_several_models(self):
        class Child(Prodict):
            name: str

        class Parent(Prodict):
            child: Child

        d = {'name': 'loop'}
        d['child'] = d
        d['me'] = d
        parent = Parent(d)
        self.assertIs(parent.me, parent)
        self.assertIsInstance(parent.child, Child)
        self.assertIs(parent.child.child, parent.child)

    def test_failed_model_leaves_no_trace(self):
        class Rejecting(Prodict):
            def __init__(self, data):
                super().__init__(data)
                raise ValueError('rejected')

        class H(Prodict):
            bad: Rejecting

        d = {}
        child = {'parent': d}
        d['child'] = child
        h = H(bad=d, child=child)
        self.assertIs(h.bad, d)
        self.assertIs(type(h.child.parent), Prodict)

    def test_from_dict_with_args_and_kwargs(self):
        class Flexible(Prodict):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

        self.assertEqual(Flexible.from_dict({'cls': 1}), {'cls': 1})
        self.assertEqual(Flexible.from_dict({'self': 2}), {'self': 2})

    def test_delete_a_read_only_property(self):
        class R(Prodict):
            @property
            def p(self):
                return 3

        r = R({'p': 99})
        with self.assertRaises(AttributeError):
            del r.p
        self.assertEqual(r['p'], 99)

    def test_conversion_that_recurses_keeps_the_value(self):
        class Endless:
            def __int__(self):
                return int(self)

        class M(Prodict):
            n: int

        value = Endless()
        self.assertIs(M(n=value).n, value)
