"""
Setup file for django_highrise.
"""
import os
from os.path import join, dirname, normpath, abspath
from setuptools import setup

# allow setup.py to be run from any path
os.chdir(normpath(join(abspath(__file__), os.pardir)))

setup(
    name='django-highrise',
    version='0.6',
    packages=['django_highrise'],
    include_package_data=True,
    install_requires=['pyrise >= 0.4', 'django >= 1.4'],
    license=open(join(dirname(__file__), 'LICENCE.md')).read(),
    description='Highrise CRM integration for Django projects.',
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    url='https://github.com/hugorodgerbrown/django-highrise',
    author='Hugo Rodger-Brown',
    author_email='hugo@rodger-brown.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
