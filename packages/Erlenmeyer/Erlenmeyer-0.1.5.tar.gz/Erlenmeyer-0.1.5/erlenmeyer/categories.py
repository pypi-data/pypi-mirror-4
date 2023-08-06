#
#  __init__.py
#  Erlenmeyer
#
#  Created by Patrick Perini on February 3, 2013.
#  See LICENSE.txt for licensing information.
#

# imports
import inspect

class category(object):
    def __init__(self, destination, override = True):
        self.destination = destination
        self.override = override
        
    def __call__(self, function):
        if not self.override and function.__name__ in dir(self.destionation):
            return
        
        if not inspect.isclass(self.destination):
            setattr(self.destination.__class__, function.__name__, function)
        else:
            setattr(self.destination, function.__name__, function)
            
def categorize(destination, function, override = True):
    category(destination, override).__call__(function)

def addCategories(destination, source, override = True, list = None):
    if not list:
        list = dir(source)
        
    for function in list:
        try:
            categorize(destination, getattr(source, function), override)
        except AttributeError, e:
            pass