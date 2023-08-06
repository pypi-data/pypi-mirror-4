# -*- coding: utf-8 -*-
from distutils.core import setup

with open("README.rst") as f:
    desc = f.read()

setup(name='letsdoit',
      version='0.1',
      description='Lets doit read tasks defined using classes, decorated '
                  'functions or function calls.',
      long_description=desc,
      author='Thomas Kluyver',
      author_email='thomas@kluyver.me.uk',
      url='https://bitbucket.org/takluyver/letsdoit',
      py_modules=['letsdoit'],
      requires=['doit (>=0.20)'],
      classifiers = [
            'License :: OSI Approved :: MIT License',
            'Topic :: Software Development :: Build Tools',
          ]
     )