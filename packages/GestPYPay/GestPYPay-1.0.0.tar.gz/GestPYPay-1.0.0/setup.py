from distutils.core import setup

setup(
    name='GestPYPay',
    version='1.0.0',
    author='Gianfranco Reppucci',
    author_email='gianfranco@gdlabs.it',
    packages=['gestpypay'],
    url='http://pypi.python.org/pypi/GestPYPay/',
    license='LICENSE.txt',
    description='Python implementation of the GestCrypt Java library',
    long_description=open('README.txt').read(),
    install_requires=[
        "requests >= 0.14.2",
    ],
)