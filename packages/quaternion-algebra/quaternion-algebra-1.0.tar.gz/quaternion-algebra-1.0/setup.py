from setuptools import Extension
from setuptools import find_packages
from setuptools import setup

setup(
    name='quaternion-algebra',
    version='1.0',
    license='GPL',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    ext_modules=[
        Extension('quaternion._quaternion', ['src/quaternion/quaternion.c'])
    ],
    test_suite = "tests.suite",
)
