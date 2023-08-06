from distutils.core import setup
from os import path

ROOT = path.dirname(__file__)
README = path.join(ROOT, 'README.rst')

setup(
    name='sef',
    py_modules = ['sef'],
    url='https://github.com/oinopion/sef',
    author='Tomek Paczkowski',
    author_email='tomek@hauru.eu',
    version='0.9',
    license='New BSD license',
    long_description=open(README).read(),
)
