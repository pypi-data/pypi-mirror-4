from setuptools import setup, find_packages
import os

version = '1.0.0-pre.2'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'ember', 'test_ember.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.ember',
    version=version,
    description="fanstatic ember.js.",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Fanstatic Developers',
    author_email='fanstatic@googlegroups.com',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'js.jquery',
        'setuptools',
        ],
    entry_points={
        'fanstatic.libraries': [
            'ember = js.ember:library',
            ],
        },
    )
