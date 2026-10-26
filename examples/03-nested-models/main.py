"""Nested dicts and lists of dicts become instances of the annotated Prodict subclasses."""
from typing import List

from prodict import Prodict


class Ram(Prodict):
    capacity: int
    unit: str


class Cpu(Prodict):
    cores: int
    clock_ghz: float


class Computer(Prodict):
    name: str
    cpu: Cpu
    rams: List[Ram]

    def total_ram(self):
        return sum(ram.capacity for ram in self.rams)


computer = Computer.from_dict({
    'name': 'Workstation',
    'cpu': {'cores': '16', 'clock_ghz': '4.2'},
    'rams': [
        {'capacity': '16', 'unit': 'GB'},
        {'capacity': 32, 'unit': 'GB'},
    ],
})

print(type(computer.cpu).__name__, computer.cpu.cores)  # Cpu 16
print(type(computer.rams[0]).__name__, computer.rams[0].capacity)  # Ram 16
assert isinstance(computer.cpu, Cpu) and computer.cpu.cores == 16
assert all(isinstance(ram, Ram) for ram in computer.rams)

# Methods on the model work on the converted values.
print(computer.total_ram())  # 48
assert computer.total_ram() == 48

# Items appended later are not converted: build them as models yourself.
computer.rams.append(Ram(capacity='64', unit='GB'))
assert computer.total_ram() == 112

print('03-nested-models: ok')
