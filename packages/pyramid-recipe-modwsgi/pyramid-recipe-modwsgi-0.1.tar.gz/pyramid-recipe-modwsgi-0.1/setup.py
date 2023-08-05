#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='pyramid-recipe-modwsgi',
    version='0.1',
    description='zc.buildout recipe to create apache modwsgi file.',
    long_description=open('README.rst').read(),
    author='Rok Garbas',
    author_email='rok@garbas.si',
    url='https://github.com/garbas/pyramid_recipe_modwsgi',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Buildout :: Recipe',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='apache pyramid wsgi buildout',
    license='MIT',
    packages=['pyramid_recipe_modwsgi'],
    zip_safe=False,
    install_requires=[
        'setuptools',
        'zc.recipe.egg',
    ],
    entry_points='''
        [zc.buildout]
        default = pyramid_recipe_modwsgi:Recipe
    ''',
)
