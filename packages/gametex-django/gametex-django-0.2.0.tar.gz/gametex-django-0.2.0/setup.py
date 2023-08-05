from distutils.core import setup

setup(
    name='gametex-django',
    version='0.2.0',
    packages=['gametex','gametex.management.commands'],
    author='Christian Ternus',
    author_email='ternus@cternus.net',
    url='http://github.com/ternus/gametex-django',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    description='Django integration for GameTeX',
    long_description=open('README.txt').read(),
)
