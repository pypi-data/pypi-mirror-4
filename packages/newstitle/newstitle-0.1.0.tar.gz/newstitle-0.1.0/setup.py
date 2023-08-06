# !/usr/bin/env python

from distutils.core import setup

setup(
      name='newstitle',
      version='0.1.0',
      packages=['newstitle', 'newstitle.gettitle'],
      author='Louie Lu',
      author_email='grapherd@gmail.com',
      license='MIT',
      install_requires=['lxml>=2.41','httplib2>=0.7.6'],
      description="Catching Taiwan Newspaper title",
      keywords ='news taiwan title',
      url='https://github.com/grapherd/newstitle'
)
