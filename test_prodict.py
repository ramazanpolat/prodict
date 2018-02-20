from typing import List, Optional, Any, Tuple
import unittest

import time

from datetime import datetime

import requests

from prodict import Prodict

tc = unittest.TestCase()


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


def test_has_attr():
    pd = SimpleKeyValue()
    assert pd == {}
    assert pd.has_attr('int_key') is True
    assert pd.has_attr('undefined key') is False


def test_dict_reserved_keys():
    with tc.assertRaises(TypeError):
        Prodict(pop=5)

    pd2 = Prodict(pop1=5)
    with tc.assertRaises(TypeError):
        pd2.pop = 5


def test_attr_initial_value_is_none():
    pd = SimpleKeyValue()
    assert pd.int_key is None
    assert pd.str_key is None
    assert pd.float_key is None


def test_setting_and_getting_attrs():
    pd = SimpleKeyValue()
    pd.int_key = 1
    pd.str_key = 'str'
    pd.float_key = 1.23
    assert pd.int_key == 1
    assert pd.str_key == 'str'
    assert pd.float_key == 1.23


def test_setting_unannotated_keys():
    pd = SimpleKeyValue()
    pd.dynamic_int = 0
    pd.dynamic_str = 'dynamic_str_value'
    pd.dynamic_float = 0.123

    assert pd.dynamic_int == 0
    assert pd.dynamic_str == 'dynamic_str_value'
    assert pd.dynamic_float == 0.123


# def test_default_values():
#     if 1 == 1:
#         raise NotImplemented
#     pd = SimpleKeyDefaultValue()
#     assert pd.has_attr('int_key')
#     assert pd.has_attr('str_key')
#     assert pd.has_attr('float_key')
#     assert pd.int_key == 1
#     assert pd.str_key == 'default str'
#     assert pd.float_key == 1.234
#     pd.int_key = 2
#     print('pd.int_key = ', pd.int_key)
#     pd.str_key = 'new'
#     pd.float_key = 2.345
#
#     assert pd.int_key == 2
#     assert pd.str_key == 'new'
#     assert pd.float_key == 2.345


def test_annotated_constructor():
    pd = SimpleKeyValue(int_key=0, str_key='str', float_key=1.234)
    print(pd)
    assert pd == {'int_key': 0, 'str_key': 'str', 'float_key': 1.234}
    assert set(pd.attr_names()) == {'int_key', 'str_key', 'float_key'}


def test_dynamic_constructor():
    pd = SimpleKeyValue(int_key=0, str_key='str', float_key=1.234, dyn_int_key=1, dyn_str_key='dyn_str',
                        dyn_float_key=2.345)
    print(pd)
    assert pd == {'int_key': 0, 'str_key': 'str', 'float_key': 1.234, 'dyn_int_key': 1, 'dyn_str_key': 'dyn_str',
                  'dyn_float_key': 2.345}
    assert set(pd.attr_names()) == {'int_key', 'str_key', 'float_key'}


def test_load_annotated_attrs_from_dict():
    sample_dict = {'int_key': 0, 'str_key': 'str value', 'float_key': 1.234}
    pd: SimpleKeyValue = SimpleKeyValue.from_dict(sample_dict)
    assert pd.int_key == 0
    assert pd.str_key == 'str value'
    assert pd.float_key == 1.234


def test_load_dynamic_attrs_from_dict():
    sample_dict = {'dynamic_int': 0, 'dynamic_str': 'str value', 'dynamic_float': 1.234}
    pd: SimpleKeyValue = SimpleKeyValue.from_dict(sample_dict)
    assert pd.dynamic_int == 0
    assert pd.dynamic_str == 'str value'
    assert pd.dynamic_float == 1.234


def test_annotated_attr_names():
    pd = SimpleKeyValue()
    assert set(pd.attr_names()) == {'int_key', 'str_key', 'float_key'}


def test_advanced_attr_names():
    pd = AdvancedKeyValue()
    assert pd == {}
    assert set(pd.attr_names()) == {'tuple_key', 'list_key', 'dict_key'}


def test_setting_and_getting_advanced_attrs():
    pd = AdvancedKeyValue()
    assert pd == {}
    assert set(pd.attr_names()) == {'tuple_key', 'list_key', 'dict_key'}

    pd.tuple_key = (1, 2)
    pd.list_key = [1, 2, 3]
    pd.dict_key = {'int_key': 0, 'str_key': 'str_value', 'float_key': 1.234}
    assert pd.tuple_key == (1, 2)
    assert pd.list_key == [1, 2, 3]
    assert pd.dict_key == {'int_key': 0, 'str_key': 'str_value', 'float_key': 1.234}

    print('pd.tuple_key =', pd.tuple_key)
    print('pd.list_key =', pd.list_key)
    print('pd.dict_key =', pd.dict_key)
    print('type(pd.dict_key) =', type(pd.dict_key))


def test_list_annotation():
    pd = ListProdict()
    assert pd == {}
    assert set(pd.attr_names()) == {'li', 'li_int', 'li_str'}

    pd.li = [1, 2, 3]
    pd.li_int = [1, 2, 3]
    pd.li_str = ['a', 'b', 'c']

    assert pd.li == [1, 2, 3]
    assert pd.li_int == [1, 2, 3]
    assert pd.li_str == ['a', 'b', 'c']


def test_recursive_annotations1():
    r = Recursive()
    assert r == {}
    assert set(r.attr_names()) == {'prodict_key', 'simple_key'}

    r.prodict_key = Prodict(a=1)
    print('r.prodict_key =', r.prodict_key)
    print('r.prodict_key.a =', r.prodict_key.a)
    print('type(r.prodict_key) =', type(r.prodict_key))
    assert r.prodict_key == {'a': 1}
    assert r.prodict_key.a == 1
    assert type(r.prodict_key) == Prodict


def test_recursive_annotations2():
    r = Recursive()

    assert set(r.attr_names()) == {'prodict_key', 'simple_key'}

    r.simple_key = SimpleKeyValue(int_key=0, str_key='str', float_key=1.234, dyna_key='dynamic_value')
    print('r.simple_key =', r.simple_key)
    print('r.simple_key.int_key =', r.simple_key.int_key)
    print('r.simple_key.str_key =', r.simple_key.str_key)
    print('r.simple_key.float_key =', r.simple_key.float_key)
    print('r.simple_key.dyna_key =', r.simple_key.dyna_key)
    print('type(r.simple_key) =', type(r.simple_key))

    assert r.simple_key == {'int_key': 0, 'str_key': 'str', 'float_key': 1.234, 'dyna_key': 'dynamic_value'}
    assert set(r.simple_key.attr_names()) == {'int_key', 'str_key', 'float_key'}
    assert type(r.simple_key) == SimpleKeyValue


def test_recursive_annotations3():
    r = Recursive()

    r.dynamic_dict_attr = {'a': 1, 'b': 2, 'c': 3}
    r.dynamic_prodict_attr = Prodict.from_dict({'a': 1, 'b': 2, 'c': 3})

    assert r.dynamic_dict_attr == {'a': 1, 'b': 2, 'c': 3}
    assert type(r.dynamic_dict_attr) == Prodict

    assert r.dynamic_prodict_attr == {'a': 1, 'b': 2, 'c': 3}
    assert type(r.dynamic_prodict_attr) == Prodict


class AnyType(Prodict):
    # x=1 type: Any
    a: Any
    b: Tuple
    c: Any


def test_any_type():
    at = AnyType()
    at.a = 1
    print(at.a)

    at.b = (1, 2, 3)
    print(at.b)


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
        if self.rams2:
            return sum([ram.capacity for ram in self.rams2])
        return 0


def test_deep_recursion_from_dict():
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
    print('computer =', computer)
    print('type(computer.dict_key) =', type(computer.dict_key))
    print('computer.brand =', computer.brand)
    print('computer.cpu =', computer.cpu)
    print('type(computer.cpu) =', type(computer.cpu))
    print('type(computer.rams) =', type(computer.rams))
    print('computer.rams[0] =', computer.rams[0])
    print('type(computer.rams[0]) =', type(computer.rams[0]))
    print('Total ram =', computer.total_ram())
    print('Total ram2 =', computer.total_ram2())

    print("computer['rams'] =", computer['rams'])
    print("type(computer['rams']) =", type(computer['rams']))
    print("computer['rams'][0] =", computer['rams'][0])


def test_bracket_access():
    pd = SimpleKeyValue()
    pd.str_key = 'str_value_123'
    assert pd['str_key'] == pd.str_key
    assert pd.get('str_key') == pd.str_key


def test_null_assignment():
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


def test_multiple_instances():
    class Multi(Prodict):
        a: int
        b: str

    m1 = Multi()
    m1.a = 1

    m2 = Multi()
    m2.a = 2

    print(m1)
    print(m2)


def test_property():
    class PropertyClass(Prodict):
        bid: float
        ask: float
        last: float

        @property
        def spread(self) -> float:
            return self.ask - self.bid

        @property
        def spread_percent(self) -> float:
            return 100 * (self.ask - self.bid) / self.last

    btc_usdt = PropertyClass()
    btc_usdt.bid = 10000
    btc_usdt.ask = 12000
    btc_usdt.last = 10000
    print(btc_usdt.spread)
    print(btc_usdt.spread_percent)


if __name__ == '__main__':
    start_time = datetime.now().timestamp()

    test_has_attr()
    test_attr_initial_value_is_none()
    test_setting_and_getting_attrs()
    test_setting_unannotated_keys()
    test_load_annotated_attrs_from_dict()
    test_load_dynamic_attrs_from_dict()
    test_annotated_attr_names()
    test_advanced_attr_names()
    test_setting_and_getting_advanced_attrs()
    test_list_annotation()
    test_dynamic_constructor()
    test_annotated_constructor()
    test_recursive_annotations1()
    test_recursive_annotations2()
    test_recursive_annotations3()
    test_dict_reserved_keys()
    test_deep_recursion_from_dict()
    test_bracket_access()
    test_null_assignment()
    test_any_type()
    test_multiple_instances()
    test_property()

    end_time = datetime.now().timestamp()

    print('Whole test suite took {} seconds.'.format(end_time - start_time))
