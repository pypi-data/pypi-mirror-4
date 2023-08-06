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
    version='0.0.7dev',
    packages=find_packages(),
    include_package_data=True,
    url='http://marcos.org.do',
    license='BSD',
    author='Eneldo Antonio Serrata Peralta',
    author_email='eneldoserrata@gmail.com',
    description='ERP apps Flask container',
    install_requires=[
        'Flask>=0.9',
        'WTForms-Alchemy>=0.2.5',
        'Flask-SQLAlchemy>=0.16',
        'Flask-Security>=1.5.4',
        'Flask-Restless>=0.9.3',
        'Flask-WTF>=0.8.2',
        'Flask-Script>=0.5.3'

    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points="""
            [console_scripts]
            marcos-project=flask_marcos.bin.marcos_project:create_project
        """,
)
