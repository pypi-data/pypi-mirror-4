# !/usr/bin/env python

from distutils.core import setup

setup(
      name='pyUnihan',
      version='0.0.1',
      packages=['pyunihan', 'pyunihan.database'],
      author='Louie Lu',
      author_email='grapherd@gmail.com',
      license='MIT',
      description="A lookup for unihan",
      keywords ='unihan cjk radical stroke chinese',
      url='https://github.com/grapherd/pyunihan',      
      classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
)
