#coding: utf-8
from distutils.core import setup
import os
import sys


def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
magma_dir = 'magma'

for dirpath, dirnames, filenames in os.walk(magma_dir):
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

version = __import__('magma').VERSION

setup(
    name = "magma-framework",
    version = version,
    author = 'Marek Waluś',
    author_email = 'marekwalus@gmail.com',
    description = 'A lightweight Python web framework',
    packages = packages,
    scripts = ['magma/magma-admin.py'],
    data_files = data_files,
    classifiers = [
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
   ],
)