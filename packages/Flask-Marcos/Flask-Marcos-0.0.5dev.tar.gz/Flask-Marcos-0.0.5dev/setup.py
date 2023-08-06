"""
Flask-Marcos
------------

Flask-Marcos es un contenedor de aplicaciones para negocios creado sobre Flask un webdevelopment framework.


Es facil de instalar y empesar a utilizar
`````````````````````````````````````````

::

    $ pip install Flask-Marcos
    $ marcos-project hello_word
    $ cd hello_word
    $ python run.py


Links
`````

* `website <http://marcos.org.do/>`_
* `documentation <http://docs.marcos.ogg.do/>`_
* `development version
  <https://github.com/eneldoserrata/Flask-Marcos>`_

"""

from distutils.core import setup
from setuptools import find_packages


setup(
    name='Flask-Marcos',
    version='0.0.5dev',
    packages=find_packages(),
    include_package_data=True,
    url='http://marcos.org.do',
    license='BSD',
    author='Eneldo Antonio Serrata Peralta',
    author_email='eneldoserrata@gmail.com',
    description='ERP apps Flask container',
    install_requires=[
        'Flask>=0.9',
        'Flask-SQLAlchemy>=0.16',
        'Flask-Security>=1.5.4',
        'Flask-Restless>=0.9.3',
        'Flask-WTF>=0.8.2',
        'Flask-Script>=0.5.3'

    ],
    entry_points="""
            [console_scripts]
            marcos-project=flask_marcos.bin.marcos_project:create_project
        """,
)
