from typing import List

from prodict import Prodict

# Example 0: Use it like regular `dict`, because **it is** a dict

p = Prodict(lang='Python', pros='Rocks!')
print(p)  # {'lang': 'Python', 'pros': 'Rocks!'}

p2 = Prodict.from_dict({'Hello': 'world'})

print(p2)  # {'Hello': 'world'}

print(issubclass(Prodict, dict))  # True

print(isinstance(p, dict))  # True

print(set(dir(dict)).issubset(dir(Prodict)))  # True


# Example 1: Type hinting

class Country(Prodict):
    name: str
    population: int


turkey = Country()
turkey.name = 'Turkey'
turkey.population = 79814871

# Example 2: Auto type conversion

germany = Country(name='Germany', population='82175700', flag_colors=['black', 'red', 'yellow'])

print(germany.population)  # 82175700
print(type(germany.population))  # <class 'int'>

print(germany.flag_colors)  # ['black', 'red', 'yellow']
print(type(germany.population))  # <class 'int'>


# Example 3: Recursive object instantiation
class Ram(Prodict):
    capacity: int
    unit: str
    type: str
    clock: int


class Computer(Prodict):
    name: str
    cpu_cores: int
    rams: List[Ram]

    def total_ram(self):
        return sum([ram.capacity for ram in self.rams])


comp1 = Computer.from_dict(
    {
        'name':
            'My Computer',
        'cpu_cores': 4,
        'rams': [
            {'capacity': 4,
             'unit': 'GB',
             'type': 'DDR3',
             'clock': 2400}
        ]
    })
print(comp1.rams)  # [{'capacity': 4, 'type': 'DDR3'}]

comp1.rams.append(Ram(capacity=8, type='DDR3'))
comp1.rams.append(Ram.from_dict({'capacity': 12, 'type': 'DDR3', 'clock': 2400}))

print(comp1.rams)
# [
#   {'capacity': 4, 'unit': 'GB', 'type': 'DDR3', 'clock': 2400},
#   {'capacity': 8, 'type': 'DDR3'},
#   {'capacity': 12, 'type': 'DDR3', 'clock': 2400}
# ]

print(type(comp1.rams))
print(type(comp1.rams[0]))