#coding: utf-8
from distutils.core import setup
import os

def fullsplit(path, result=None):
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
tool_dir = 'resttouch'

for dirpath, dirnames, filenames in os.walk(tool_dir):
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

setup(
    name = "resttouch",
    version = '0.1',
    author = u'Marek Waluś',
    author_email = 'marekwalus@gmail.com',
    description = 'REST client',
    packages = packages,
    data_files = data_files,
    classifiers = [
        'Environment :: Web Environment',
        'Programming Language :: Python',
   ],
)
