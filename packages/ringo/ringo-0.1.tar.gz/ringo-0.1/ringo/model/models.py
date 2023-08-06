# Import model from ringo
from ringo.model import DBSession, Base
from ringo.model.base import BaseItem
from sqlalchemy import Column, Integer, Text

# Add your custom declarative class defintions.
class MyModel(Base, BaseItem):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    value = Column(Integer)

    def __init__(self, name, value):
        self.name = name
        self.value = value
