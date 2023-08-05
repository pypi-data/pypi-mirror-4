from sys import path
import os
from setuptools import setup
#from distutils.core import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'django-smoke-admin',
    version = '0.1.2',
    packages = ['django-smoke-admin'],
    include_package_data = True,
    license = 'MIT License',
    description = 'django-smoke-admin tests that all admin pages for all registered models responds correctly (HTTP 200).',
    long_description = README,
    url = 'https://bitbucket.org/Melevir/django-smoke-admin',
    author = 'Lebedev Ilya',
    author_email = 'melevir@gmail.com',
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
)