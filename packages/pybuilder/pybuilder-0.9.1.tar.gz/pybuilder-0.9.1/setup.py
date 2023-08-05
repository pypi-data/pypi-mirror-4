#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'pybuilder',
          version = '0.9.1',
          description = 'An extendible, easy to use continuous build tool for Python',
          long_description = '''
python-builder is a continuous build tool for multiple languages.

python-builder primarily targets Python projects but due to its extendible
nature it can be used for other languages as well.

python-builder features a powerful yet easy to use plugin mechanism which 
allows programmers to extend the tool in an unlimited way.  
''',
          author = "Alexander Metzner, Michael Gruber, Udo Juettner",
          author_email = "alexander.metzner@gmail.com, aelgru@gmail.com, udo.juettner@gmail.com",
          license = 'Apache License',
          url = 'http://pybuilder.github.com',
          scripts = ['pyb'],
          packages = ['pythonbuilder', 'pythonbuilder.plugins', 'pythonbuilder.plugins.python'],
          classifiers = ['Development Status :: 3 - Alpha', 'Environment :: Console', 'Intended Audience :: Developers', 'License :: OSI Approved :: Apache Software License', 'Programming Language :: Python', 'Topic :: Software Development :: Build Tools', 'Topic :: Software Development :: Quality Assurance', 'Topic :: Software Development :: Testing'],
          
          
          
          
          zip_safe=True
    )
