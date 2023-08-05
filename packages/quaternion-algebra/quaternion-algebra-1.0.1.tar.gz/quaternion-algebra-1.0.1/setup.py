from setuptools import Extension
from setuptools import find_packages
from setuptools import setup

setup(
    name='quaternion-algebra',
    version='1.0.1',
    license='GPL',
    url='https://bitbucket.org/sirex/quaternion',
    description='Quaternion algebra for Python.',
    long_description=open('README.rst').read(),
    package_dir={'': 'src'},
    packages=find_packages('src'),
    ext_modules=[
        Extension('quaternion._quaternion', ['src/quaternion/quaternion.c'])
    ],
    test_suite = "tests.suite",
)
