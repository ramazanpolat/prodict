# Prodict
Prodict = Dictionary with IDE friendly(auto code completion) and dot-accessible attributes and more.

# Motivation
Ever wanted to use a `dict` like a class and access keys as attributes? Prodict does exactly this. 

Although there are number of modules doing this, Prodict does a little bit more.

You can provide type hints and get auto code completion!

With type hints, you also get recursive object instantiations, which will blow your mind.

You will never want to use `dict` again.

# Comparison with regular `dict`

Without `Prodict`:
```python
class Post:
    def __init(self, text, date):
        self.text = text
        self.date = date
        
class User:
    def __init(self, user_id, user_name, posts):
        self.user_id = user_id
        self.user_name = user_name
        self.posts:List[Post] = posts
       
user_json = requests.get("https://some.restservice.com/user/1").json()

posts = [Post(post['text'], post['date']) for post in user_json['posts']]
user = User(user_json['user_id'], user_json['user_name'], posts)
```

With `Prodict`:
```python
class Post(Prodict):
    text: str
    date: str
        
class User(Prodict):
    user_id: int
    user_name: str
    posts:List[Post]
       
user_json = requests.get("https://some.restservice.com/user/1").json()
user = User.from_dict(user_json)
```

# Features

  1) A class with dynamic properties, without defining it beforehand.

```python
j = Prodict()
j.hi = 'there'
```

  2) Pass named arguments and all arguments will become properties.

```python
p = Prodict(lang='Python', pros='Rocks!')
print(p.lang)  # Python
print(p.pros)  # Rocks!
print(p)  # {'lang': 'Python', 'pros': 'Rocks!'}
```

  3) Instantiate from a `dict`, get `dict` keys as properties
```python
p = Prodict.from_dict({'lang': 'Python', 'pros': 'Rocks!'})
print(p.lang)   # Python
p.another_property = 'this is dynamically added'
```

  4) Pass a `dict` as argument, get a nested `Prodict`!
```python
p = Prodict(package='Prodict', makes='Python', rock={'even': 'more!'})
print(p)  #  {'package': 'Prodict', 'makes': 'Python', 'rock': {'even': 'more!'}}
print(type(p.rock))  # <class 'prodict.Prodict'>
```

  5) Extend `Prodict` and use type annotations for auto type conversion and auto code completion
```python
class User(Prodict):
    user_id: int
    name: str

user = User(user_id="1", "name":"Ramazan")
type(user.user_id) # <class 'int'>
# IDE will be able to auto complete 'user_id' and 'name' properties(see example 1 below)
```
Why type conversion? Because it will be useful if the incoming data doesn't have the desired type.

```python
class User(Prodict):
    user_id: int
    name: str
    
response = requests.get("https://some.restservice.com/user/1").json()
post: RestResponse = RestResponse.from_dict(response)
type(post.user_id) # <class 'int'>
# post.user_id will be an `int`, even if rest service responded with `str`.
# Same goes for all built-in types(int, str, float)
```

# Examples

Example 0: Use it like regular `dict`, because **it is** a dict.
```python

from prodict import Prodict

p = Prodict(lang='Python', pros='Rocks!')
print(p)  # {'lang': 'Python', 'pros': 'Rocks!'}

p2 = Prodict.from_dict({'Hello': 'world'})

print(p2)  # {'Hello': 'world'}

print(issubclass(Prodict, dict))  # True

print(isinstance(p, dict))  # True

print(set(dir(dict)).issubset(dir(Prodict)))  # True


```
Example 1: Accessing keys as attributes and auto completion.
```python
from prodict import Prodict
class Country(Prodict):
    name: str
    population: int

turkey = Country()
turkey.name = 'Turkey'
turkey.population = 79814871
```

![auto code complete](/auto-complete1.png?raw=true "Auto complete in action!")

Example 2: Auto type conversion
```python
germany = Country(name='Germany', population='82175700', flag_colors=['black', 'red', 'yellow'])

print(germany.population)  # 82175700
print(type(germany.population))  # <class 'int'> <-- The type is `int` !
# If you don't want type conversion and still want to have auto code completion, use `Any` as type.
print(germany.flag_colors)  # ['black', 'red', 'yellow']
print(type(germany.population))  # <class 'int'>
```

Example 3: Recursive object instantiation
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
print(type(comp1.rams))  # <class 'list'>
print(type(comp1.rams[0]))  # <class 'Ram'> <-- Mind the type !
```

# Limitations
- You cannot use names of dict methods as attribute names.
- Requires Python 3.6+

# Thanks
I would like to thank to [JetBrains](https://www.jetbrains.com/) for creating [PyCharm](https://www.jetbrains.com/pycharm/), the IDE that made my life better.

