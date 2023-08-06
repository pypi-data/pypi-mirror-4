from distutils.core import setup
from setuptools import find_packages

setup(
    name='django_keyval',
    version='0.1.1',
    author='Edwin van Opstal',
    author_email='evo.se-technology.com',
#    packages=['django_keyval',],
    url='http://github.com/EdwinvO/django_keyval',
    license='LICENSE.txt',
    description='Simple django key-value store',
    long_description=open('README.rst').read(),
    install_requires=[
        "Django >= 1.1.1",
    ],
    packages=find_packages(),
)
