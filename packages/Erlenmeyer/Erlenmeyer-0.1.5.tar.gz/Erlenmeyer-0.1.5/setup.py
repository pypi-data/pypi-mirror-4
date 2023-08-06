from distutils.core import setup

setup(
    name = 'Erlenmeyer',
    version = '0.1.5',
    author = 'Patrick Perini',
    author_email = 'pperini@megabitsapp.com',
    packages = [
        'erlenmeyer',
        'erlenmeyer.ext'
    ],
    scripts = [
        'bin/erlenmeyer',
        'bin/erlenmeyer_templates/erlenmeyer.project.tmpl.py',
        'bin/erlenmeyer_templates/handlers/erlenmeyer.ModelObjectHandler.tmpl.py',
        'bin/erlenmeyer_templates/models/erlenmeyer.ModelObject.tmpl.py',
        'bin/erlenmeyer_templates/documentation/erlenmeyer.server.tmpl.html',
        'bin/erlenmeyer_templates/settings/erlenmeyer.settings.tmpl.json'
    ],
    url = 'http://MegaBits.github.com/Erlenmeyer',
    license = 'LICENSE.txt',
    description = 'Automatically generate Flask servers from Core Data.',
    long_description = open('README.txt').read(),
    install_requires = [
        'Flask >= 0.9',
        'Flask-SQLAlchemy >= 0.16',
        'Jinja2 >= 2.6'
    ]
)