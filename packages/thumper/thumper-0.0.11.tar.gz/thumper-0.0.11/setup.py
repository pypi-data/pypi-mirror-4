'''install script for thumper library'''
from setuptools import setup, Command


class PyTest(Command):
    '''implement py.test standalone testing via python setup.py test'''
    user_options = []

    def initialize_options(self):
        '''none needed'''
        pass

    def finalize_options(self):
        '''none needed'''
        pass

    def run(self):
        '''implement the command'''
        import sys, subprocess
        errno = subprocess.call([sys.executable, 'thumper/runtests.py'])
        raise SystemExit(errno)

setup(
    name='thumper',
    version='0.0.11',
    author='Jeff Hinrichs',
    author_email='jeffh@dundeemt.com',
    packages=['thumper', 'thumper.test' ],
    #scripts=['bin/stowe-towels.py','bin/wash-towels.py'],
    url='https://bitbucket.org/dundeemt/thumper',
    license='LICENSE.txt',
    description='Simplifies interactions with RabbitMQ by focusing on design patterns based on Topic Exchanges.',
    long_description=open('README.rst').read(),
    install_requires=[
        "amqplib >=1.0.2",
        "pyyaml == 3.10",
    ],
    cmdclass = {'test': PyTest},
)