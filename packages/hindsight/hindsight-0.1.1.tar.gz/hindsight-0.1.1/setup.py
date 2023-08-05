from setuptools import setup

setup(
    name='hindsight',
    version='0.1.1',
    packages=['hindsight'],
    summary='Hindsight Software Python Tools',
    author='Jack Bastow',
    author_email='jack.bastow@hindsightsoftware.co.uk',
    url='http://pypi.python.org/pypi/hindsight/',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.txt').read(),
    install_requires=['requests'],
    requires=['requests'],
    entry_points={
        'console_scripts': [
            'behave-cli = hindsight.cli:main'
        ]
    }
)