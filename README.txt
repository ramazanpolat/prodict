# Prodict
Prodict = Dictionary with IDE friendly(auto code completion) and dot-accessible attributes

# Motivation
Ever wanted to use a `dict` like a class and access keys as attributes? Prodict does exactly this. 

Although there are number of modules doing this, Prodict does a little bit more.

You can provide type hints and get auto-complete!

Auto complete in action:

![auto code complete](/auto-complete1.png?raw=true "Auto complete in action!")

# Examples

Example 1:
```python
class Country(Prodict):
    name: str
    population: int


turkey = Country()
turkey.name = 'Turkey'
turkey.population = 79814871
```

Example 2:
```python
germany = Country(name='Germany', population=82175700, flag_colors=['black', 'red', 'yellow'])

print(germany.flag_colors)  # ['black', 'red', 'yellow']
print(type(germany.flag_colors)) # <class 'list'>
```

Example 3:
```python
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


comp1 = Computer.from_dict({'name': 'My Computer', 'cpu_cores': 4})
print(comp1)
# {'name': 'My Computer', 'cpu_cores': 4}

comp1.rams = []
comp1.rams.append(Ram(capacity=8, unit='GB', type='DDR3', clock=2400))
comp1.rams.append(Ram.from_dict({'capacity': 4, 'unit': 'GB', 'type': 'DDR3', 'clock': 2400}))

print(comp1)
# {
#   'name': 'My Computer',
#   'cpu_cores': 4, 
#   'rams': [
#       {'capacity': 8, 'unit': 'GB', 'type': 'DDR3', 'clock': 2400},
#       {'capacity': 4, 'unit': 'GB', 'type': 'DDR3', 'clock': 2400}
#   ]
# }

print(comp1.rams)
#   [
#       {'capacity': 8, 'unit': 'GB', 'type': 'DDR3', 'clock': 2400},
#       {'capacity': 4, 'unit': 'GB', 'type': 'DDR3', 'clock': 2400}
#   ]
```


# Limitations
- You cannot use names of dict methods as attribute names.
- Requires Python 3.6+

