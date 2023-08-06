from setuptools import setup, find_packages
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='pickle_converter',
    version = '0.1',
    author = 'Mate Gabri',
    author_email = 'mate@gabri.hu',
    description = ('Python pickle converter for data portability.'),
    license = 'BSD',
    keywords = 'python pickle json converter',
    url = 'http://packages.python.org/pickle_converter',
    long_description = read('README.md'),
    classifiers = [
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Topic :: Utilities",
    ],
    packages = find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'pickle_converter = pickle_converter.main:main',
            ],
        },
)
