import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'geoprisma_config',
    version = '0.0.1',
    packages = ['geoprisma_config'],
    include_package_data = True,
    license = 'BSD License',
    description = 'A Django app to help configure a postgresql geoprisma system',
    long_description = README,
    url = 'https://github.com/solution-globale-informatique/geoprisma_config',
    author = 'Alexandre Lessard',
    author_email = 'alexandrel@solutionglobale.com',
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)