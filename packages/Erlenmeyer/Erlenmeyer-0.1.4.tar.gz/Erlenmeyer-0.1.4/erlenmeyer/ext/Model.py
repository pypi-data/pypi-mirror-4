#
#  Model.py
#  Erlenmeyer
#
#  Created by Patrick Perini on February 7, 2013.
#  See LICENSE.txt for licensing information.
#

# imports
from flask.ext.sqlalchemy import SQLAlchemy

# constants 
classMethods = [
    'all',
    'get',
]

instanceMethods = [
    '__iter__',
    'update',
    'save',
    'delete'
]

# class accessors
def all(self):
    return self.query.all()
    
def get(self, identifier):
    return self.query.get(identifier)

# accessors
def __iter__(self):
    for key in self.__dict__:
        if not key.startswith('_'):
            yield (key, self.__dict__[key])

# mutators
def update(self, properties):
    for key in properties:
        value = properties[key] if type(properties[key]) != list else properties[key][0]
        setattr(self, key, value)

def save(self):
    self.__class__.__database__.session.add(self)
    self.__class__.__database__.session.commit()
    
def delete(self):
    self.__class__.__database__.session.delete(self)
    self.__class__.__database__.session.commit()