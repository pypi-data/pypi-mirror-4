#
#  jinja2.py
#  Erlenmeyer
#
#  Created by Patrick Perini on February 6, 2013.
#  See LICENSE.txt for licensing information.
#

# imports
import re

# filters
def camelcase(value):
    value = list(value)
    value[0] = value[0].upper()
    value = ''.join(value)
    return value
    
def underscore(value):
    value = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', value)
    value = re.sub('([a-z0-9])([A-Z])', r'\1_\2', value).lower()
    return value