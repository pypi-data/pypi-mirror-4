#!/usr/bin/env python
import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


description = "Buildout recipe for Qooxdoo projects."

recipes = [
    'default = mdvorak.recipe.qooxdoo:ScriptRecipe',
    'script = mdvorak.recipe.qooxdoo:ScriptRecipe',
    'run = mdvorak.recipe.qooxdoo:RunRecipe',
]

setup(
    name="mdvorak.recipe.qooxdoo",
    version='1.0',
    keywords='buildout recipe qooxdoo',
    entry_points={'zc.buildout': recipes},
    url='https://bitbucket.org/mdvorak/qooxdoo-recipe/wiki/Home',
    author='Michal Dvorak',
    author_email='mikee@mdvorak.org',
    license='Simplified BSD License',
    description=description,
    long_description=read('README.rst'),
    packages=find_packages(),
    namespace_packages=['mdvorak', 'mdvorak.recipe'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
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
