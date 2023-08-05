from distutils.core import setup
import os

# Silly hack because the README.rst file isn't included in the
def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

setup(
    name='pywunder',
    version='0.0.1',
    author='Alex Good',
    author_email='alexjsgood@gmail.com',
    packages=['pywunder'],
    url='http://pypi.python.org/pypi/pywunder/',
    license='LICENSE.txt',
    description='Very simple wrapper around the wunderground weather API',
    long_description=read('README'),
    install_requires=[
        'requests'
    ],
    test_suite='test'
)
