from setuptools import setup, find_packages
import os

# The version of the wrapped library is the starting point for the
# version number of the python package.
# In bugfix releases of the python package, add a '-' suffix and an
# incrementing integer.
# For example, a packaging bugfix release version 1.4.4 of the
# js.jquery package would be version 1.4.4-1 .

version = '0.2.1'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.rst')
    + '\n' +
    read('js', 'unicode_eastasianwidth', 'test_unicode_eastasianwidth.txt')
    )

setup(
    name='js.unicode_eastasianwidth',
    version=version,
    description="Fanstatic packaging of Counting the unicode characters based Unicode East Asian Width database for JavaScript. It includes some tools for dealing with characters.",
    long_description=long_description,
    classifiers=[
      "Programming Language :: Python :: 2.6",
      "Programming Language :: Python :: 2.7",
      "Programming Language :: Python :: 3.2",
      "Programming Language :: Python :: Implementation :: PyPy",
    ],
    keywords='',
    license='MIT',
    packages=find_packages(),namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'setuptools',
        'js.angular',
        ],
    entry_points={
        'fanstatic.libraries': [
            'unicode_eastasianwidth = js.unicode_eastasianwidth:library',
            ],
        },
    )
