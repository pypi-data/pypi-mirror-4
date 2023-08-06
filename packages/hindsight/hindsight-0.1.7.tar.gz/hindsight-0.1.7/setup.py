from setuptools import setup

setup(
    name='hindsight',
    version='0.1.7',
    packages=['hindsight'],
    description='Python tools for Hindsight Software',
    author='Jack Bastow',
    author_email='jack.bastow@hindsightsoftware.co.uk',
    url='http://pypi.python.org/pypi/hindsight/',
    license='MIT License',
    long_description=open('README.txt').read(),
    install_requires=['requests'],
    requires=['requests'],
    entry_points={
        'console_scripts': [
            'behave-cli = hindsight.cli:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development"
    ],
    use_2to3=True
)