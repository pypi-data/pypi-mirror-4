#
#  {{ metadata.fileName }}
#  {{ metadata.projectName }}
#
#  Created by {{ metadata.fileAuthor }} on {{ metadata.pubDate }} via Erlenmeyer.
#  Copyright (c) {{ metadata.pubYear }} {{ metadata.projectOwner }}. All rights reserved.
#

# imports
import os
import json
import flask
from erlenmeyer import categories
from flask.ext.sqlalchemy import SQLAlchemy
from erlenmeyer.ext import Model as ModelExtensions
from erlenmeyer.ext import SQLAlchemy as SQLAlchemyExtensions

# globals
__filepath__ = os.path.dirname(os.path.abspath(__file__))
settings = json.load(open('%s/settings/settings.json' % (__filepath__)))

flaskApp = flask.Flask(__name__)
flaskApp.config['SQLALCHEMY_DATABASE_URI'] = {{ metadata.databaseURL }}

database = SQLAlchemy(flaskApp)
categories.addCategories(database, SQLAlchemyExtensions, list = SQLAlchemyExtensions.instanceMethods)
categories.addCategories(database.Model.__class__, ModelExtensions, list = ModelExtensions.classMethods)
categories.addCategories(database.Model, ModelExtensions, list = ModelExtensions.instanceMethods)

{% if metadata.includeProcessors -%}
# processors
def preprocessRequest(request):
    pass
{% endif %}

# handlers
{% for model in models -%}
# - {{ model.className }}
@flaskApp.route("/{{ model.className }}s", methods = ["GET", "PUT"])
def handle{{ model.className }}s():
    from handlers import {{ model.className }}Handler
    
    {% if metadata.includeProcessors -%}
    preprocessRequest(flask.request)
    {% endif %}
    
    if flask.request.method == "GET":
        return {{ model.className }}Handler.get{{ model.className|camelcase }}s(**dict(flask.request.args))
        
    elif flask.request.method == "PUT":
        return {{ model.className }}Handler.put{{ model.className|camelcase }}(dict(flask.request.form))
        
@flaskApp.route("/{{ model.className }}s/<{{ model.primaryKey }}>", methods = ["GET", "POST", "DELETE"])
def handle{{ model.className }}({{ model.primaryKey }}):
    from handlers import {{ model.className }}Handler
    
    {% if metadata.includeProcessors -%}
    preprocessRequest(flask.request)
    {% endif %}

    if flask.request.method == "GET":
        return {{ model.className }}Handler.get{{ model.className|camelcase }}({{ model.primaryKey }})
        
    elif flask.request.method == "POST":
        return {{ model.className }}Handler.post{{ model.className|camelcase }}({{ model.primaryKey }}, dict(flask.request.form))
        
    elif flask.request.method == "DELETE":
        return {{ model.className }}Handler.delete{{ model.className|camelcase }}({{ model.primaryKey }})
        
{% for relationship in model.relationships -%}
# - - {{ relationship.name }}
{% if relationship.isToMany -%}
@flaskApp.route("/{{ model.className }}s/<{{ model.primaryKey }}>/{{ relationship.name }}", methods = ["GET", "PUT", "DELETE"])
def handle{{ model.className }}{{ relationship.name|camelcase }}({{ model.primaryKey }}):
    from handlers import {{ model.className }}Handler

    {% if metadata.includeProcessors -%}
    preprocessRequest(flask.request)
    {% endif %}

    if flask.request.method == "GET":
        return {{ model.className }}Handler.get{{ model.className|camelcase }}{{ relationship.name|camelcase }}({{ model.primaryKey }})
        
    elif flask.request.method == "PUT":
        return {{ model.className }}Handler.put{{ model.className|camelcase }}{{ relationship.name|camelcase }}({{ model.primaryKey }}, flask.request.form['{{ relationship.name }}Object'])
        
    elif flask.request.method == "DELETE":
        return {{ model.className }}Handler.delete{{ model.className|camelcase }}{{ relationship.name|camelcase }}({{ model.primaryKey }}, flask.request.args['{{ relationship.name }}Object'])
        
{% else -%}
@flaskApp.route("/{{ model.className }}s/<{{ model.primaryKey }}>/{{ relationship.name }}", methods = ["GET", "POST"])
def handle{{ model.className }}{{ relationship.name|camelcase }}({{ model.primaryKey }}):
    from handlers import {{ model.className }}Handler
    
    {% if metadata.includeProcessors -%}
    preprocessRequest(flask.request)
    {% endif %}
    
    if flask.request.method == "GET":
        return {{ model.className }}Handler.get{{ model.className|camelcase }}{{ relationship.name|camelcase }}({{ model.primaryKey }})
        
    elif flask.request.method == "POST":
        return {{ model.className }}Handler.post{{ model.className|camelcase }}{{ relationship.name|camelcase }}({{ model.primaryKey }}, flask.request.form['{{ relationship.name }}Object'])

{% endif -%}
{% else %}
# - - no relationships...

{% endfor %}
{% else %}
# - no models...

{% endfor %}

# functions
def createTables():
    from {{ metadata.projectName }} import database
    {% for model in models -%}
    from models.{{ model.className }} import {{ model.className }}
    {% endfor %}
    
    database.create_all()

# main
if __name__ == "__main__":    
    createTables()

    flaskApp.run(
        host = settings['server']['ip'],
        port = settings['server']['port'],
        debug = settings['server']['debug']
    )