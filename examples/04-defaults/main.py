"""Set default values in init(), a hook Prodict calls from its own __init__."""
from typing import List

from prodict import Prodict


class Settings(Prodict):
    retries: int
    timeout: float
    tags: List[str]

    def init(self):
        # Runs before the keyword arguments are applied, so they win.
        self.retries = 3
        self.timeout = 10.0
        self.tags = []


defaults = Settings()
print(defaults)  # {'retries': 3, 'timeout': 10.0, 'tags': []}
assert defaults == {'retries': 3, 'timeout': 10.0, 'tags': []}

custom = Settings(retries='5', verbose=True)
print(custom)  # {'retries': 5, 'verbose': True, 'timeout': 10.0, 'tags': []}
assert custom.retries == 5  # the argument replaced the default, and was converted
assert custom.timeout == 10.0  # untouched default
assert custom.verbose is True  # unannotated keys are allowed too

# Each instance gets its own default list.
defaults.tags.append('fast')
assert Settings().tags == []

print('04-defaults: ok')
