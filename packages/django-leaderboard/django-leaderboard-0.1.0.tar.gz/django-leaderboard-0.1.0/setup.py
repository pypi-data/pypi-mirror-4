# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-leaderboard',
    version='0.1.0',
    author=u'Suleyman Melikoglu',
    author_email='suleyman@melikoglu.info',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/laplacesdemon/django-leaderboard',
    license='BSD licence, see LICENCE.txt',
    description='A Django leaderboard (scoreboard) app, using redis as its backend',
    long_description=open('README.md').read(),
    zip_safe=False,
)
