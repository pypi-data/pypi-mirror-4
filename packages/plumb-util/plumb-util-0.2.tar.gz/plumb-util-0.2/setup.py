from setuptools import setup, find_packages

setup(
    name="plumb-util",
    version = '0.2',
    maintainer='Luminoso, LLC',
    maintainer_email='dev@lumino.so',
    license = "MIT",
    url = 'http://github.com/LuminosoInsight/plumb_util',
    platforms = ["any"],
    description = "Plumbing utility library",
    packages=find_packages(),
    install_requires=['dnspython'],
)
