from setuptools import setup, find_packages
import os

# The version of the wrapped library is the starting point for the
# version number of the python package.
# In bugfix releases of the python package, add a '-' suffix and an
# incrementing integer.
# For example, a packaging bugfix release version 1.4.4 of the
# js.jquery package would be version 1.4.4-1 .

version = '1.0.1'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.rst')
    + '\n' +
    read('js', 'd3_cloud', 'test_d3_word_cloud.txt')
    + '\n' +
    read('CHANGES.rst'))

setup(
    name='js.d3_cloud',
    version=version,
    description="Fanstatic packaging of D3 Word Cloud Layout",
    long_description=long_description,
    classifiers=[],
    keywords='word cloud tag visualization canvas wordle d3',
    author='Fanstatic Developers',
    author_email='fanstatic@googlegroups.com',
    url='https://github.com/davidjb/js.d3_cloud',
    license='BSD',
    packages=find_packages(),namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    setup_requires=[
        'setuptools-git',
        'minify',
    ],
    install_requires=[
        'fanstatic',
        'setuptools',
        'js.d3',
        ],
    entry_points={
        'fanstatic.libraries': [
            'd3_word_cloud = js.d3_cloud:library',
            ],
        },
    )
