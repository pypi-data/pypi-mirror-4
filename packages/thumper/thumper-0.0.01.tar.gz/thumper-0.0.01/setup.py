'''install script for thumper library'''
from setuptools import setup

setup(
    name='thumper',
    version='0.0.01',
    author='Jeff Hinrichs',
    author_email='jeffh@dundeemt.com',
    packages=['thumper', 'thumper.test' ],
    #scripts=['bin/stowe-towels.py','bin/wash-towels.py'],
    url='http://pypi.python.org/pypi/thumper/',
    license='LICENSE.txt',
    description='Useful RabbitMQ stuff.',
    long_description=open('README.rst').read(),
    install_requires=[
        "amqplib >=1.0.2",
        "pyyaml == 3.10",
    ],
)