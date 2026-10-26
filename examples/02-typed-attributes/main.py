"""Annotate a Prodict subclass to get IDE completion and automatic type conversion."""
from typing import Any

from prodict import Prodict


class Country(Prodict):
    name: str
    population: int
    area_km2: float
    raw: Any  # Any: no conversion, but the IDE still knows the attribute


# Values are converted to the annotated type on assignment.
germany = Country(name='Germany', population='83200000', area_km2='357588', raw='83200000')
print(germany.population, type(germany.population).__name__)  # 83200000 int
print(germany.area_km2, type(germany.area_km2).__name__)  # 357588.0 float
assert germany.population == 83200000
assert germany.area_km2 == 357588.0
assert germany.raw == '83200000'  # Any keeps the value as it came

# Assignment after construction converts too.
germany.population = '84000000'
assert germany.population == 84000000

# Annotated attributes that were not given are present with the value None.
turkey = Country(name='Turkey')
print(turkey)  # {'name': 'Turkey', 'population': None, 'area_km2': None, 'raw': None}
assert turkey.population is None

# Keys without an annotation are kept as they are (dicts would become Prodicts).
germany.flag_colors = ['black', 'red', 'gold']
assert germany.flag_colors == ['black', 'red', 'gold']

print('02-typed-attributes: ok')
