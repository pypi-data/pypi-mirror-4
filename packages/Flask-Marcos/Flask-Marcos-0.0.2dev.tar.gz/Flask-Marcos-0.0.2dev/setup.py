from distutils.core import setup
from setuptools import find_packages

setup(
    name='Flask-Marcos',
    version='0.0.2dev',
    packages=find_packages(),
    include_package_data=True,
    url='http://marcos.org.do',
    license='BSD',
    author='Eneldo Antonio Serrata Peralta',
    author_email='eneldoserrata@gmail.com',
    description='ERP apps Flask container',
    install_requires=[
        'Flask==0.9',
        'Flask-SQLAlchemy==0.16',
        'Flask-Security==1.5.4',
        'Flask-Restless==0.9.3',
        'Flask-WTF==0.8.2',
        'WTForms-Alchemy==0.2.5',
        'Flask-Script==0.5.3'

    ],
    entry_points="""
            [console_scripts]
            marcos-project=flask_marcos.bin.marcos_project:create_project
        """,
)


"""Notas sobre las dependencias de los paquetes requeridos

    Flask
    install_requires=[
        'Werkzeug>=0.7',
        'Jinja2>=2.4',
        'itsdangerous>=0.17'
    ]

    Flask-SQLAlchemy
    install_requires=[
        'setuptools',
        'Flask',
        'SQLAlchemy'
    ]

    Flask-Security
    install_requires=[
        'Flask>=0.9',
        'Flask-Login>=0.1.3',
        'Flask-Mail>=0.7.3',
        'Flask-Principal>=0.3.3',
        'Flask-WTF>=0.8',
        'itsdangerous>=0.17',
        'passlib>=1.6.1',
    ]

    Flask-Restless
    requirements = [
        'flask>=0.7',
        'SQLAlchemy'
    ]

    WTForms-Alchemy
    install_requires=[
        'SQLAlchemy==0.7.8',
        'WTForms==1.0.2'
    ]

    Flask-WTF
    install_requires=[
        'Flask',
        'WTForms>=1.0'
    ]

    Flask-Bootstrap
    install_requires=[
        'Flask>=0.8'
    ]

    Flask-Script
    install_requires = ['Flask']
    if sys.version_info < (2, 7):
        install_requires += ['argparse']


"""