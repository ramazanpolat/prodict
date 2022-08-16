# Prodict
Prodict = Dictionary with IDE friendly(auto code completion) and dot-accessible attributes **and more**.

# What it does
Ever wanted to use a `dict` like a class and access keys as attributes? **Prodict** does exactly this. 

Although there are number of modules doing this, **Prodict** does a little bit **more**.

You can provide type hints and get auto code completion!

With type hints, you also get nested object instantiations, which will blow your mind.

You will never want to use `dict` again.

# Why?
* Because accessing `dict` keys like `d['key']` is error prone and ugly.

* Because it becomes uglier if it is nested, like `d['key1]['key2']['key3']`. Compare `d['key1]['key2']['key3']` to `d.key1.key2.key3`, which one looks better?

* Because since web technologies mostly talk with JSON, it should be much more easy to use JSON data(see sample use case below).

* Because auto code completion makes developers' life easier.

* Because serializing a Python class to `dict` and deserializing from `dict` in one line is awesome!
 

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
print(p.rock.even)  #  'more!'
print(type(p.rock))  # <class 'prodict.Prodict'>
```

  5) Extend `Prodict` and use type annotations for auto type conversion and auto code completion
```python
class User(Prodict):
    user_id: int
    name: str

user = User(user_id="1", name="Ramazan")
type(user.user_id) # <class 'int'>
# IDE will be able to auto complete 'user_id' and 'name' properties(see example 1 below)
```
Why type conversion? Because it will be useful if the incoming data doesn't have the desired type.

```python
class User(Prodict):
    user_id: int
    name: str
    literal: Any
    
response = requests.get("https://some.restservice.com/user/1").json()
user: User = User.from_dict(response)
type(user.user_id) # <class 'int'>
```

**Notes on automatic type conversion**:
* In the above example code, `user.user_id` will be an `int`, even if rest service responded with `str`.
* Same goes for all built-in types(int, str, float, bool, list, tuple), except `dict`. Because by default, all `dict` types will be converted to `Prodict`.
* If you don't want any type conversion but still want to have auto code completion, use `Any` as type annotation, like the `literal` attribute defined in `User` class.
* If the annotated type of an attribute is sub-class of a `Prodict`, the provided `dict` will be instantiated as the instance of sub-class. Even if it is `List` of the sub-class(see sample usa case below).



# Sample use case

Suppose that you are getting this JSON response from `https://some.restservice.com/user/1`:

```javascript
{
  user_id: 1,
  user_name: "rambo",
  posts: [
    {
      title:"Hello World",
      text:"This is my first blog post...",
      date:"2018-01-02 03:04:05",
      comments: [
          {
            user_id:2,
            comment:"Good to see you blogging",
            date:"2018-01-02 03:04:06"
          },
          {
            user_id:3,
            comment:"Good for you",
            date:"2018-01-02 03:04:07"
          }
        ]
    },
    {
      title:"Leave the old behind",
      text:"Stop using Python 2.x...",
      date:"2018-02-03 04:05:06",
      comments: [
          {
            user_id:4,
            comment:"Python 2 is dead, long live Python",
            date:"2018-02-03 04:05:07"
          },
          {
            user_id:5,
            comment:"You are god damn right :wears Heissenberg glasses:",
            date:"2018-02-03 04:05:08"
          }
        ]
    }
  ]
}
```
Despite the fact that JSON being schemaless, most REST services will respond with a certain structure.
In the above example, the structure is something like this:
```
User
 |--> user_id
 |--> user_name
 |--> posts [post]
       |--> title
       |--> text
       |--> date
       |--> comments [comment]
             |--> user_id
             |--> comment
             |--> date
```

And you want to convert this to appropriate Python classes.

Without `Prodict`:

```python
class Comment:
	def __init__(self, user_id, comment, date):
    	self.user_id = user_id
    	self.comment = comment
        self.date = date
        
class Post:
    def __init__(self, title, text, date):
    	self.title = title
        self.text = text
        self.date = date
        self.comments = []
        
class User:
    def __init__(self, user_id, user_name):
        self.user_id = user_id
        self.user_name = user_name
        self.posts = []

user_json = requests.get("https://some.restservice.com/user/1").json()
posts = [Post(post['title'], post['text'], post['date']) for post in user_json['posts']]
for post in posts:
    post.comments = [[comment for comment in post['comments']] for post in user_json['posts']]

user = User(user_json['user_id'], user_json['user_name'])
user.posts = posts

for post in user.posts:
    print(post.title)

```

With **Prodict** you just need to define the classes and let the prodict do the rest like this:

```python
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

user_json = requests.get("https://some.restservice.com/user/1").json()
user:User = User.from_dict(user_json)
# Don't forget to annotate the `user` with `User` type in order to get auto code completion.
```

See the difference?
Plus you can add new attributes to `User`, `Post` and `Comment` objects dynamically and access them as dot-accessible attributes.


# Examples

**Example 0**: Use it like regular `dict`, because **it is** a dict.
```python

from prodict import Prodict

d = dict(lang='Python', pros='Rocks!')
p = Prodict(lang='Python', pros='Rocks!')

print(d)  # {'lang': 'Python', 'pros': 'Rocks!'}
print(p)  # {'lang': 'Python', 'pros': 'Rocks!'}
print(d == p)  # True

p2 = Prodict.from_dict({'Hello': 'world'})

print(p2)  # {'Hello': 'world'}
print(issubclass(Prodict, dict))  # True
print(isinstance(p, dict))  # True
print(set(dir(dict)).issubset(dir(Prodict)))  # True
```

**Example 1**: Accessing keys as attributes and auto completion.
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

**Example 2**: Auto type conversion
```python
germany = Country(name='Germany', population='82175700', flag_colors=['black', 'red', 'yellow'])

print(germany.population)  # 82175700
print(type(germany.population))  # <class 'int'> <-- The type is `int` !
# If you don't want type conversion and still want to have auto code completion, use `Any` as type.
print(germany.flag_colors)  # ['black', 'red', 'yellow']
print(type(germany.population))  # <class 'int'>
```

**Example 3**: Nested class instantiation
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
        'name': 'My Computer',
        'cpu_cores': 4,
        'rams': [
            {'capacity': 4,
             'unit': 'GB',
             'type': 'DDR3',
             'clock': 2400}
        ]
    })
print(comp1.rams)  #  [{'capacity': 4, 'unit': 'GB', 'type': 'DDR3', 'clock': 2400}]

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

**Example 4**: Provide default values

You can use `init` method to provide default values. Keep in mind that `init` is NOT `__init__` but `init` method will be called in `__init__` method.

Additionally, you can use `init` method instead of `__init__` without referring to `super`.

```python
class MyDataWithDefaults(Prodict):
    an_int: int
    a_str: str
    
    def init(self):
        self.an_int = 42
        self.a_str = 'string'
        

data = MyDataWithDefaults(dynamic=43)
print(data)
# {'an_int':42, 'a_str':'string', 'dynamic':43}

``` 

# Class attributes vs Instance attributes

Prodict only works for instance attributes.
Even if you try to set an inherited class attribute, a new instance attribute is created and set.

Consider this example:
```python
from prodict import Prodict

class MyClass(Prodict):
    class_attr: int = 42  # class_attr is a class attribute, not instance attribute

my_class = MyClass()
print(f"my_class.class_attr: {my_class.class_attr}")  # 42
# There is no 'class_attr' defined as instance attribute, so class attribute will be returned (42).
print(f"MyClass.class_attr: {MyClass.class_attr}") # 42
# This is a class attribute, it will be returned as is.

# Now an instance attribute 'class_attr' is created and set to 77
my_class.class_attr = 77
print(f"my_class.class_attr: {my_class.class_attr}")  # 42
# For this matter, avoid setting class_attribute with dot notation, use class name instead

MyClass.class_attr = 88
print(f"MyClass.class_attr: {my_class.class_attr}")  # 88

# So where did 77 go? It is in instance attribute of the class and since it's name is colliding with
# the class attribute, you can't get it by dot notation. You can use .get tho.
print(f"my_class.get('class_attr'): {my_class.get('class_attr')}")  # 77
```


# Installation
If your default Python is 3.7:

`pip install prodict`

If you have more than one Python versions installed:

`python3.7 -m pip install prodict`


# Limitations
- You cannot use `dict` method names as attribute names because of ambiguity.
- You cannot use `Prodict` method names as attribute names(I will change `Prodict` method names with dunder names to reduce the limitation).
- You must use valid variable names as `Prodict` attribute names(obviously). For example, while '1' cannot be an attribute for `Prodict`, it is perfectly valid for a `dict` to have '1' as a key. You can still use prodict.set_attribute('1',123) tho.
- Requires Python 3.7+

# Thanks
I would like to thank to [JetBrains](https://www.jetbrains.com/) for creating [PyCharm](https://www.jetbrains.com/pycharm/), the IDE that made my life better.

