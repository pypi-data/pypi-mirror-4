from distutils.core import setup

setup(
    name='rsr-reverse',
    version='0.1.1',
    author='Cuzzo Yahn',
    author_email='yahn007@gmail.com',
    packages=['rsr_reverse', 'rsr_reverse.test'],
    url='http://github.com/cuzzo/rsr-reverse',
    license='LICENSE.txt',
    description='RSR Reverse is a Rails-style route reverser.',
    long_description=open('README.txt').read(),
)
