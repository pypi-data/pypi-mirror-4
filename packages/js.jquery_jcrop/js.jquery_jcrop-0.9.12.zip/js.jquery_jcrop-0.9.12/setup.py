from setuptools import setup, find_packages
import os

# The version of the wrapped library is the starting point for the
# version number of the python package.
# In bugfix releases of the python package, add a '-' suffix and an
# incrementing integer.
# For example, a packaging bugfix release version 1.4.4 of the
# js.jquery package would be version 1.4.4-1 .

version = '0.9.12'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.rst')
    + '\n' +
    read('js', 'jquery_jcrop', 'test_jcrop.txt')
    + '\n' +
    read('CHANGES.rst'))

setup(
    name='js.jquery_jcrop',
    version=version,
    description="Fanstatic packaging of jCrop",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Fanstatic Developers',
    author_email='fanstatic@googlegroups.com',
    url='https://github.com/davidjb/js.jquery_jcrop',
    license='BSD',
    packages=find_packages(),namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'setuptools',
        'js.jquery',
        ],
    entry_points={
        'fanstatic.libraries': [
            'jcrop = js.jquery_jcrop:library',
            ],
        },
    )
