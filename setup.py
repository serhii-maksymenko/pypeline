from setuptools import setup, find_packages


setup(
    name='pypeline',
    version='1.0.0',
    description='Framework for constructing parallel pipelines on top of multiprocessing framework.',
    long_description=open('README.md').read(),
    author='Serhii Maksymenko',
    packages=find_packages()
)