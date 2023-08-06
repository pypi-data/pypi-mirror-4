from distutils.core import setup

setup(
    name='RockPy',
    version='0.1.0',
    author='MWR Volk',
    author_email='volk@geophysik.uni-muenchen.de',
    packages=['RockPy'],
    scripts=[],
    url='http://pypi.python.org/pypi/RockPy/',
    license='LICENSE.txt',
    description='A collection of Functions for Paleo- and Rock-magnetic Analysis.',
    long_description=open('README.txt').read(),
    install_requires=[
        "Django >= 1.1.1",
        "caldav == 0.1.4",
    ],
)