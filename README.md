# Prodict
Prodict = Dictionary with IDE friendly(auto code completion), dot-accessible attributes

# Motivation
Ever wanted to use a `dict` like a class and access keys as attributes? Prodict does exactly this. 

Although there are number of modules doing this, Prodict does a little bit more.

You can provide type hints and get auto-complete!

Auto complete in action:

![auto code complete](/auto-complete1.png?raw=true "Auto complete in action!")

# Examples

Example 1:
```
class Country(Prodict):
    name: str
    population: int


turkey = Country()
turkey.name = 'Turkey'
turkey.population = 79814871
```

# Limitations
You cannot use names of dict methods as attribute names.

