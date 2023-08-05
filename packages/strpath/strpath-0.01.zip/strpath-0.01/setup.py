from distutils.core import setup
from glob import glob
import os


long_desc="""
strpath is a usable proof-of-concept for having a path object based on the str type.

Example usage:

    from path import Path

    --> job = Path(r'c:/orders/12345/')
    --> table = job / 'abc67890.dbf'
    --> table
    Path('c:\\orders\\12345\\abc67890.dbf')
    --> table.path
    Path('c:\\orders\\12345\\')
    --> table.filename
    Path('abc67890.dbf')
    --> table.basename
    Path('abc67890')
    --> table.ext
    Path('.dbf')
    --> dest = table.replace('c:/orders','//another_machine/orders')
    --> dest
    Path('\\\\another_machine\\orders\\12345\\abc67890.dbf')
"""

setup( name='strpath',
       version= '0.01',
       license='BSD License',
       description='Proof-of-concept for Path objects based on the str type',
       long_description=long_desc,
       url='http://groups.google.com/group/python-dbase',
       py_modules=['strpath'],
       provides=['Path'],
       author='Ethan Furman',
       author_email='ethan@stoneleaf.us',
       classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python', ],
     )

