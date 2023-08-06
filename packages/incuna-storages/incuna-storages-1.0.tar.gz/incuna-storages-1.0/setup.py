from setuptools import setup, find_packages

import incuna_storages


setup(
    name='incuna-storages',
    packages=find_packages(),
    include_package_data=True,
    version=incuna_storages.__version__,
    description='A collection of django storage backends.',
    long_description=open('README.rst').read(),
    author=incuna_storages.__author__,
    author_email='admin@incuna.com',
    url='https://github.com/incuna/incuna-storages/',
    zip_safe=False,
)

