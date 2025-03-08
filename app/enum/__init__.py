from enum import Enum


class FormEnum(Enum):
    @classmethod
    def choices(cls):
        return [(choice, choice.value) for choice in cls]

    @classmethod
    def coerce(cls, item):
        return cls(item) if not isinstance(item, cls) else item

    def __str__(self):
        return str(self.value)
