# coding: utf8

from distutils.core import setup
import os
import re

project_dir = 'accountant'


def parse_requirements(file_name):
    requirements = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'(\s*#)|(\s*$)', line):
            continue
        if re.match(r'\s*-e\s+', line):
            requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
        elif re.match(r'\s*-f\s+', line):
            pass
        else:
            requirements.append(line)

    return requirements


def parse_dependency_links(file_name):
    dependency_links = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'\s*-[ef]\s+', line):
            dependency_links.append(re.sub(r'\s*-[ef]\s+', '', line))

    return dependency_links

packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)


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


for dirpath, dirnames, filenames in os.walk(project_dir):
    # Ignore PEP 3147 cache dirs and those whose names start with '.'
    dirnames[:] = [
        d for d in dirnames if not d.startswith('.') and d != '__pycache__'
    ]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([
            dirpath, [os.path.join(dirpath, f) for f in filenames]
        ])


setup(
    name='django-accountant',
    version='0.1.2',
    description='Django based account manager.',
    author='Ron Elliott',
    author_email='ronaldbelliott@gmail.com',
    install_requires=parse_requirements('requirements.txt'),
    dependency_links=parse_dependency_links('requirements.txt'),
    packages=packages,
    data_files=data_files,
)
