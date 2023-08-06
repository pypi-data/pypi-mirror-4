#
#  {{ metadata.fileName }}
#  {{ metadata.projectName }}
#
#  Created by {{ metadata.fileAuthor }} on {{ metadata.pubDate }} via Erlenmeyer.
#  Copyright (c) {{ metadata.pubYear }} {{ metadata.projectOwner }}. All rights reserved.
#

# imports
import json
import flask
from models import {{ model.className }}
{% for relationship in model.relationships -%}
from models import {{ relationship.className }}
{% endfor %}

# handlers
def get{{ model.className|camelcase }}s(**kwargs):
    """
    Returns a list of all {{ model.className }}s.
        
    @return: A flask response built with a JSON list of all {{ model.className }}s.
    """
    
    for key in kwargs:
        if type(kwargs[key]) == list:
            kwargs[key] = kwargs[key][0]
    
    all{{ model.className|camelcase }}s = {{ model.className }}.{{ model.className }}.all(**kwargs)
    all{{ model.className|camelcase }}sDictionaries = [dict({{ model.className|lower }}) for {{ model.className|lower }} in all{{ model.className|camelcase }}s if dict({{ model.className|lower }})]
    
    return flask.Response(
        response = json.dumps(all{{ model.className|camelcase }}sDictionaries),
        status = 200,
        content_type = 'application/json'
    )
    
def put{{ model.className|camelcase }}(properties):
    """
    Inserts a new {{ model.className }} with the given properties into the database.
        
    @param properties: A series of key-value pairs to apply to the new {{ model.className }}.
    
    @return: An empty flask response.
    """
    
    {{ model.primaryKey }} = properties['{{ model.primaryKey }}']
    if type({{ model.primaryKey }}) == list:
        {{ model.primaryKey }} = {{ model.primaryKey }}[0]
    
    {{ model.className|lower }} = {{ model.className }}.{{ model.className }}.get({{ model.primaryKey }})
    if not {{ model.className|lower }}:
        {{ model.className|lower }} = {{ model.className }}.{{ model.className }}()
    
    {{ model.className|lower }}.update(properties)    
    {{ model.className|lower }}.save()
    
    return flask.Response(
        response = '',
        status = 200,
        content_type = 'application/json'
    )
    
def get{{ model.className|camelcase }}({{ model.primaryKey }}):
    """
    Returns the {{ model.className }} with the given {{ model.primaryKey }}.
        
    @param {{ model.primaryKey }}: The {{ model.primaryKey }} identifying the desired {{ model.className }}.
    
    @return: An empty flask response with status 404 if the desired {{ model.className }} cannot be found. A flask response built with the JSON dictionary for the desired {{ model.className }} otherwise.
    """
    
    {{ model.className|lower }} = {{ model.className }}.{{ model.className }}.get({{ model.primaryKey }})
    if not {{ model.className|lower }}:
        return flask.Response(
            response = '',
            status = 404,
            content_type = 'application/json'
        )
        
    {{ model.className|lower }}Dictionary = dict({{ model.className|lower }})
    
    return flask.Response(
        response = json.dumps({{ model.className|lower }}Dictionary),
        status = 200,
        content_type = 'application/json'
    )
    
def post{{ model.className|camelcase }}({{ model.primaryKey }}, properties):
    """
    Updates the {{ model.className }} with the given {{ model.primaryKey }} to have the given properties.
        
    @param {{ model.primaryKey }}: The {{ model.primaryKey }} identifying the desired {{ model.className }}.
    @param properties: A series of key-value pairs to apply to the desired {{ model.className }}.
    
    @return: An empty flask response with status 404 if the desired {{ model.className }} cannot be found. An empty flask response with status 200 otherwise.
    """
    
    {{ model.className|lower }} = {{ model.className }}.{{ model.className }}.get({{ model.primaryKey }})
    if not {{ model.className|lower }}:
        return flask.Response(
            response = '',
            status = 404,
            content_type = 'application/json'
        )
        
    {{ model.className|lower }}.update(properties)        
    {{ model.className|lower }}.save()
    
    return flask.Response(
        response = '',
        status = 200,
        content_type = 'application/json'
    )
    
def delete{{ model.className|camelcase }}({{ model.primaryKey }}):
    """
    Deletes the {{ model.className }} with the given {{ model.primaryKey }}.
        
    @param {{ model.primarKey }}: The {{ model.primaryKey }} identifying the desired {{ model.className }}.
    
    @return: An empty flask reponse with status 404 if the desired {{ model.className }} cannot be found. An empty flask response with status 200 otherwise.
    """
    
    {{ model.className|lower }} = {{ model.className }}.{{ model.className }}.get({{ model.primaryKey }})
    if not {{ model.className|lower }}:
        return flask.Response(
            response = '',
            status = 404,
            content_type = 'application/json'
        )
        
    {{ model.className|lower }}.delete()
    
    return flask.Response(
        response = '',
        status = 200,
        content_type = 'application/json'
    )
    
# - relationships
{% for relationship in model.relationships -%}
{% if relationship.isToMany -%}
def get{{ model.className|camelcase }}{{ relationship.name|camelcase }}({{ model.primaryKey }}):
    """
    Returns the {{ relationship.name }} of the {{ model.className }} with the given {{ model.primaryKey }}.
    
    @param {{ model.primaryKey }}: The {{ model.primaryKey }} identifying the desired {{ model.className }}.
    
    @return: An empty flask reponse with status 404 if the desired {{ model.className }} cannot be found. A flask response with the JSON list of the {{ relationship.name }} of the desired {{ model.className }}.
    """
    
    {{ model.className|lower }} = {{ model.className }}.{{ model.className }}.get({{ model.primaryKey }})
    if not {{ model.className|lower }}:
        return flask.Response(
            response = '',
            status = 404,
            content_type = 'application/json'
        )
        
    {{ relationship.name }}Dictionaries = []
    for {{ relationship.className|lower }} in {{ model.className|lower }}.{{ relationship.name }}:
        {{ relationship.className|lower }}Dictionary = dict({{ relationship.className|lower }})
        
        {{ relationship.name }}Dictionaries.append({{ relationship.className|lower }}Dictionary)
        
    return flask.Response(
        response = json.dumps({{ relationship.name }}Dictionaries),
        status = 200,
        content_type = 'application/json'
    )
    
def put{{ model.className|camelcase }}{{ relationship.name|camelcase }}({{ model.primaryKey }}, {{ relationship.name }}{{ model.primaryKey|camelcase }}):
    """
    Adds the given {{ relationship.name }}{{ model.primaryKey|camelcase }} to the desired {{ model.className }}'s {{ relationship.name }}.
        
    @param {{ model.primaryKey }}: The {{ model.primaryKey }} identifying the desired {{ model.className }}.
    @param {{ relationship.name }}{{ model.primaryKey|camelcase }}: The {{ model.primaryKey }} to add to the desired {{ model.className }}'s {{ relationship.name }}.
    
    @return: An empty flask reponse with status 404 if the desired {{ model.className }} cannot be found. An empty flask response with status 200 otherwise.
    """
    
    {{ model.className|lower }} = {{ model.className }}.{{ model.className }}.get({{ model.primaryKey }})
    if not {{ model.className|lower }}:
        return flask.Response(
            response = '',
            status = 404,
            content_type = 'application/json'
        )
    
    {{ relationship.className|lower }} = {{ relationship.className }}.{{ relationship.className }}.get({{ relationship.name }}{{ model.primaryKey|camelcase }})
    if not {{ relationship.className|lower }}:
        return flask.Response(
            response = '',
            status = 400,
            content_type = 'application/json'
        )
    
    if {{ relationship.className|lower }} not in {{ model.className|lower }}.{{ relationship.name }}:
        {{ model.className|lower }}.{{ relationship.name }}.append({{ relationship.className|lower }})
    
    {{ model.className|lower }}.save()
        
    return flask.Response(
        response = '',
        status = 200,
        content_type = 'application/json'
    )
    
def delete{{ model.className|camelcase }}{{ relationship.name|camelcase }}({{ model.primaryKey }}, {{ relationship.name }}{{ model.primaryKey|camelcase }}):
    """
    Removes the given {{ relationship.name }}{{ model.primaryKey|camelcase }} from the desired {{ model.className }}'s {{ relationship.name }}.
        
    @param {{ model.primaryKey }}: The {{ model.primaryKey }} identifying the desired {{ model.className }}.
    @param {{ relationship.name }}{{ model.primaryKey|camelcase }}: The {{ model.primaryKey }} to remove from the desired {{ model.className }}'s {{ relationship.name }}.
    
    @return: An empty flask reponse with status 404 if the desired {{ model.className }} cannot be found. An empty flask response with status 200 otherwise.
    """
    
    {{ model.className|lower }} = {{ model.className }}.{{ model.className }}.get({{ model.primaryKey }})
    if not {{ model.className|lower }}:
        return flask.Response(
            response = '',
            status = 404,
            content_type = 'application/json'
        )
    
    {{ relationship.className|lower }} = {{ relationship.className }}.{{ relationship.className }}.get({{ relationship.name }}{{ model.primaryKey|camelcase }})
    if not {{ relationship.className|lower }}:
        return flask.Response(
            response = '',
            status = 400,
            content_type = 'application/json'
        )
    
    if {{ relationship.className|lower }} in {{ model.className|lower }}.{{ relationship.name }}:
        {{ model.className|lower }}.{{ relationship.name }}.remove({{ relationship.className|lower }})
    
    {{ model.className|lower }}.save()
        
    return flask.Response(
        response = '',
        status = 200,
        content_type = 'application/json'
    )
    
{% else -%}
def get{{ model.className|camelcase }}{{ relationship.name|camelcase }}({{ model.primaryKey }}):
    """
    Returns the {{ relationship.name }} of the {{ model.className }} with the given {{ model.primaryKey }}.
        
    @param {{ model.primaryKey }}: The {{ model.primaryKey }} identifying the desired {{ model.className }}.
    
    @return: An empty flask reponse with status 404 if the desired {{ model.className }} cannot be found. A flask response with the JSON representation of the {{ relationship.name }} of the desired {{ model.className }}.
    """
    
    {{ model.className|lower }} = {{ model.className }}.{{ model.className }}.get({{ model.primaryKey }})
    if not {{ model.className|lower }}:
        return flask.Response(
            response = '',
            status = 404,
            content_type = 'application/json'
        )
        
    if not {{ model.className|lower }}.{{ relationship.name }}:
        return flask.Response(
            response = json.dumps({}),
            status = 200,
            content_type = 'application/json'
        )
        
    {{ relationship.className|lower }} = {{ relationship.className }}.{{ relationship.className }}.get({{ model.className|lower }}.{{ relationship.name }})
    {{ relationship.name }}Dictionary = dict({{ relationship.className|lower }})
        
    return flask.Response(
        response = json.dumps({{ relationship.name }}Dictionary),
        status = 200,
        content_type = 'application/json'
    )
    
def post{{ model.className|camelcase }}{{ relationship.name|camelcase }}({{ model.primaryKey }}, {{ relationship.name }}{{ model.primaryKey|camelcase }}):
    """
    Sets the {{ relationship.name }} of the {{ model.className }} with the given {{ model.primaryKey }} to the given value.
        
    @param {{ model.primaryKey }}: The {{ model.primaryKey }} identifying the desired {{ model.className }}.
    @param {{ relationship.name }}{{ model.primaryKey|camelcase }}: The {{ model.primaryKey }} of the {{ relationship.name }} to set as the {{ model.className }}'s {{ relationship.name }}.
    
    @return: An empty flask reponse with status 404 if the desired {{ model.className }} cannot be found. An empty flask response with status 200 otherwise.
    """
    
    {{ model.className|lower }} = {{ model.className }}.{{ model.className }}.get({{ model.primaryKey }})
    if not {{ model.className|lower }}:
        return flask.Response(
            response = '',
            status = 404,
            content_type = 'application/json'
        )
        
    {{ relationship.className|lower }} = {{ relationship.className }}.{{ relationship.className }}.get({{ relationship.name }}{{ model.primaryKey|camelcase }})
    if not {{ relationship.className|lower }}:
        return flask.Response(
            response = '',
            status = 400,
            content_type = 'application/json'
        )
        
    {{ model.className|lower }}.{{ relationship.name }} = {{ relationship.className|lower }}.{{ model.primaryKey }}
    {{ model.className|lower }}.save()
        
    return flask.Response(
        response = '',
        status = 200,
        content_type = 'application/json'
    )
    
{% endif -%}
{% else %}
# - - no relationships ...
{% endfor %}