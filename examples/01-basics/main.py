"""A Prodict is a dict whose keys are also attributes."""
from prodict import Prodict

# Keyword arguments become keys, and every key is reachable as an attribute.
p = Prodict(lang='Python', pros='Rocks!')
print(p.lang)  # Python
print(p['pros'])  # Rocks!

# New attributes are new keys.
p.year = 1991
print(p)  # {'lang': 'Python', 'pros': 'Rocks!', 'year': 1991}

# It is a real dict: equality, isinstance and every dict method still work.
assert p == {'lang': 'Python', 'pros': 'Rocks!', 'year': 1991}
assert isinstance(p, dict)
assert sorted(p.keys()) == ['lang', 'pros', 'year']

# Build one from an existing dict. Nested dicts become Prodicts too.
config = Prodict.from_dict({'db': {'host': 'localhost', 'port': 5432}})
print(config.db.host)  # localhost
assert type(config.db) is Prodict

# A missing attribute raises AttributeError, so getattr() defaults work.
assert getattr(config, 'cache', 'no cache') == 'no cache'
try:
    config.cache
except AttributeError as error:
    print(error)  # 'Prodict' object has no attribute 'cache'

print('01-basics: ok')
