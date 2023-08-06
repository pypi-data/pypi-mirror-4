import os
#from distutils.core import setup
from setuptools import setup

PACKAGES = [
    'wsgilite',
    'wsgilite/apps',
    'wsgilite/config',
    'wsgilite/extras',
    'wsgilite/framework',
]

PACKAGE_DATA = {'wsgilite/extras': ['templates/*.rst']}


def walkfunc(arg, dir, files):
    if '__init__.py' in files:
        arg.add(dir)


if os.path.isdir('.git'):
    foundpackages = set()
    os.path.walk('wsgilite', walkfunc, foundpackages)
    if foundpackages != set(PACKAGES):
        print "Expected"
        print sorted(list(set(PACKAGES)))
        print "Found"
        print sorted(list(foundpackages))
        print "This looks funny!"


setup(
    name='wsgilite',
    version='0.1.0',
    author='dan bornside',
    author_email='dan.bornside@gmail.com',
    description='a grab-bag of web app utilities for developer convenience',
    long_description=open('README.rst').read(),
    url='https://github.com/danbornside/wsgilite',
    packages=PACKAGES,
    package_data=PACKAGE_DATA,
    entry_points={
        'console_scripts': [
            'wsgilite = wsgilite.wsgilite:main'
        ]},
    install_requires=[
        'Jinja2',
        'Pygments',
        'WebOb',
        'docutils',
        'texttable',
    ]
)
