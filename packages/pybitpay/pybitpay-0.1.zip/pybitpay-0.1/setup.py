import os

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup

try:
    here = os.path.abspath(os.path.dirname(__file__))
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
except:
    README = ''
    CHANGES = ''

setup(
    name='pybitpay',
    version='0.1',
    license='MIT',
    author='Victor Lin',
    author_email='bornstub@gmail.com',
    description='Non-official Python API for BitPay Payment Gateway API.',
    keywords='bitcoin api payment gateway bitpay',
    url='https://bitbucket.org/victorlin/pybitpay',
    zip_safe=False,
    include_package_data=True,
    packages=['bitpay'],
    install_requires=[
        'requests >= 1.2.0',
    ],
)
