from setuptools import setup

setup(
    name = 'MainApp',
    version = '0.1',
    description = 'An example of an installable program',
    author = 'q-gal',
    url = '',
    license = 'MIT',
    packages = ['test'],
    entry_points = {'console_scripts': ['prog = program.program',],},
)
