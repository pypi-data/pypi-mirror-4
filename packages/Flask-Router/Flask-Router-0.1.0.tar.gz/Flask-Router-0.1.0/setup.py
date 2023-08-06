"""
Flask-Router
==================

Install Flask-Router
"""
from setuptools import setup
import setuptools

requires = [
    'Flask',
]

setup(
    name='Flask-Router',
    version='0.1.0',
    url='http://blog.hardtack.me/',
    author='GunWoo Choi',
    author_email='6566gun@gmail.com',
    description='Tuned flask\'s URL routing library',
    long_description=__doc__,
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=requires,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
    ],
)
