from distutils.core import setup

setup(
    name='blam',
    version='0.0.1',
    author='Phil Adams',
    author_email='phil@philadams.net',
    packages=['blam', 'blam.test'],
    scripts=['bin/blam'],
    url='http://github.com/philadams/blam',
    license='LICENSE.txt',
    description='manage text snippets. on the command line.',
    long_description=open('README.txt').read(),
    install_requires=[],
)
