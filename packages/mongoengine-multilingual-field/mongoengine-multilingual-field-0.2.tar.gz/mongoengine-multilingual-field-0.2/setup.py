# This script was automatically generated by distutils2
from setuptools import setup


setup(
    name='mongoengine-multilingual-field',
    version='0.2',
    description='MongoEngine field to store MultilingualString class '
        'from i18n-string project',
    url='https://github.com/lig/mongoengine-multilingual-field',
    author='Serge Matveenko',
    author_email='s@matveenko.ru',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
    ],
    packages=['multilingual_field'],
    install_requires=['i18n_string>=0.2.1', 'mongoengine'])
