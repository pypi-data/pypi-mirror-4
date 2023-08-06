import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'readme.txt')).read()
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'django-quickview',
    version = '0.1',
    packages = ['quickview'],
    include_package_data = True,
    license = 'BSD License',
    description = 'Simple reusable package for quick scaffolding and basic views based on a given model.',
    long_description = README,
    url = 'https://bitbucket.org/weholt/django-quickview',
    author = 'Thomas A. Weholt',
    author_email = 'thomas@weholt.org',
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
    )