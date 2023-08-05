from distutils.core import setup

setup(
    name='rsr-reverse',
    version='0.1.0',
    author='Cuzzo Yahn',
    author_email='yahn007@gmail.com',
    packages=['rsrreverse', 'rsrreverse.test'],
    url='http://github.com/cuzzo/rsr-reverse',
    license='LICENSE.txt',
    description='RSR Reverse is a Rails-style route reverser.',
    long_description=open('README.txt').read(),
)
