# from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name='django-swstags',
    version='0.1.6',
    packages=find_packages(),
    license='',
    long_description=open('README.txt').read(),
    url='http://www.stoneworksolutions.net',
    author='Miguel Angel Sanchez',
    author_email='miguel.sanchez@stoneworksolutions.net',
    package_data={'': ['*.html']},
    include_package_data=True,
    install_requires=[],
    )
