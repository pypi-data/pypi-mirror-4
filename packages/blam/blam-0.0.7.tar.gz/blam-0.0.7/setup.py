from distutils.core import setup

with open('README.txt') as f:
    readme = f.read()

setup(
    name='blam',
    version='0.0.7',
    author='Phil Adams',
    author_email='phil@philadams.net',
    license='LICENSE.txt',
    long_description=readme,
    packages=['blam'],
    scripts=['bin/blam'],
    url='http://github.com/philadams/blam',
    description='manage text snippets on the command line.',
    install_requires=[],
)
