#
#  {{ metadata.fileName }}
#  {{ metadata.projectName }}
#
#  Created by {{ metadata.fileAuthor }} on {{ metadata.pubDate }} via Erlenmeyer.
#  Copyright (c) {{ metadata.pubYear }} {{ metadata.projectOwner }}. All rights reserved.
#

# imports
from {{ metadata.projectName }} import database

class {{ model.className }} (database.Model):

    # class properties
    __database__ = database

    # properties
    {% for attribute in model.attributes -%}
    {% if attribute.name == model.primaryKey -%}
    {{ attribute.name }} = database.Column(database.{{ attribute.type }}, primary_key = True)
    {% else -%}
    {{ attribute.name }} = database.Column(database.{{ attribute.type }})
    {% endif -%}
    {% else %}
    # - no properties...
    {% endfor %}
    
    # - relationships
    {% for relationship in model.relationships if not relationship.inverseHasBeenHandled -%}
    {% if relationship.isToMany -%}
    {% if relationship.inverseIsToMany -%}
    {{ relationship.name }} = database.tableRelationship(
        '{{ model.className }}',
        '{{ relationship.className }}',
        '{{ model.primaryKey }}',
        database.{{ model.primaryKeyType }},
        inverseName = '{{ relationship.inverseName }}'
    )
    {% else -%}
    {{ relationship.name }} = database.relationship('{{ relationship.className }}')
    {% endif %}
    {% else -%}
    {{ relationship.name }} = database.Column(database.{{ model.primaryKeyType }}, database.ForeignKey('{{ relationship.className|underscore }}.{{ model.primaryKey }}'))
    {% endif -%}
    {% else %}
    # - - no relationships...
    {% endfor %}