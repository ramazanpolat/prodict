import pickle
from unittest import TestCase
from typing import List, Any, Tuple
import unittest
from datetime import datetime
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
    str_key: str
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
