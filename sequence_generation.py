__all__ = ["SeqDevice","SeqSub","Seq"]

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

class SeqDevice(metaclass=ABCMeta):
    ...

class SeqSub(metaclass=ABCMeta):
    ...

class Seq(metaclass=ABCMeta):
    ...
