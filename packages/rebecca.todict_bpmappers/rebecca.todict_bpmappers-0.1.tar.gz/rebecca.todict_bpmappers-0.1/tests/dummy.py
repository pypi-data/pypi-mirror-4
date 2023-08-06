from bpmappers import Mapper, RawField
from rebecca.todict_bpmappers import bpmapper

@bpmapper('dummy.Person')
class PersonMapper(Mapper):
    username = RawField('name')
    num = RawField('value')


class Person(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

