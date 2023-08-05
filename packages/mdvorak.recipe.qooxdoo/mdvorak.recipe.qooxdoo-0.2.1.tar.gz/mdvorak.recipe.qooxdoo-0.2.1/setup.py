#!/usr/bin/env python
import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

description = "Buildout recipe for Qooxdoo projects."

recipes = [
    'default = mdvorak.recipe.qooxdoo:GeneratorRecipe',
    'generator = mdvorak.recipe.qooxdoo:GeneratorRecipe',
]

setup(
    name="mdvorak.recipe.qooxdoo",
    version='0.2.1',
    keywords='buildout recipe qooxdoo',
    entry_points={'zc.buildout': recipes},
    url='https://bitbucket.org/mdvorak/qooxdoo-recipe',
    author='Michal Dvorak',
    author_email='mikee@mdvorak.org',
    license='Simplified BSD License',
    description=description,
    long_description=read('README.rst'),
    packages=find_packages(),
    namespace_packages=['mdvorak', 'mdvorak.recipe'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=[
        'setuptools',
        'zc.buildout',
        'zc.recipe.egg',
    ]
)
