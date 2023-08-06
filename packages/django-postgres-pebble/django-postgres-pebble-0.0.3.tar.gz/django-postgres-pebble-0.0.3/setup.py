from setuptools import setup, find_packages

LONG_DESCRIPTION = ("First-class Postgre feature support for the Django ORM."
    "Includes custom extension for manually synching PG Views. For the "
    "base package, see django-postgres.")

setup(
    name='django-postgres-pebble',
    version='0.0.3',
    description="First-class Postgres feature support for the Django ORM.",
    long_description=LONG_DESCRIPTION,
    author='Scott Walton',
    author_email='scw@talktopebble.co.uk',
    license='Public Domain',
    packages=find_packages(),
    install_requires=[
        'bitstring',
        'Django>=1.3',
    ],
)
