from distutils.core import setup

setup(
    name='EmailLove',
    version='0.1.0',
    author='Ryan Detzel',
    author_email='ryandetzel@gmail.com',
    packages=['emaillove', 'emaillove.test'],
    scripts=[''],
    url='http://pypi.python.org/pypi/EmailLove/',
    license='LICENSE.txt',
    description='Useful mail provider stuff.',
    long_description=open('README.txt').read(),
    install_requires=[],
)
