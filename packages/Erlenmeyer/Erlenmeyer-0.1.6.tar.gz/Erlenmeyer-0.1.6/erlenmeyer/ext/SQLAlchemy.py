#
#  SQLAlchemy.py
#  Erlenmeyer
#
#  Created by Patrick Perini on February 10, 2013.
#  See LICENSE.txt for licensing information.
#

# imports
from erlenmeyer.ext import jinja2 as jinja2Extensions

# constants
instanceMethods = [
    'tableRelationship'
]

# accessors
def tableRelationship(self, sourceClassName, destinationClassName, primaryKeyName, primaryKeyType, inverseName = None):
    sourceTableName = jinja2Extensions.underscore(sourceClassName)
    destinationTableName = jinja2Extensions.underscore(destinationClassName)

    backReference = self.backref(inverseName) if inverseName else None

    relationshipTable = self.Table(
        '%s_%s' % (sourceTableName, destinationTableName),
        self.Column(sourceTableName, primaryKeyType, self.ForeignKey('%s.%s' % (sourceTableName, primaryKeyName))),
        self.Column(destinationTableName, primaryKeyType, self.ForeignKey('%s.%s' % (destinationTableName, primaryKeyName)))
    )
    
    return self.relationship(destinationClassName, secondary = relationshipTable, backref = backReference)