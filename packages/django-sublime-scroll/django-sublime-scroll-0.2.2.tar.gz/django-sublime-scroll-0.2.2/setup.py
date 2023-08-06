#!/usr/bin/env python

from setuptools import setup
import os
import setuplib

packages, package_data = setuplib.find_packages('sublime_scroll')

setup(
    name='django-sublime-scroll',
    version=__import__('sublime_scroll').__version__,
    author='Arnar Yngvason',
    author_email='arnar1@gmail.com',
    license='BSD License',
    platforms=['OS Independent'],
    packages=packages,
    package_data=package_data,
    url='https://github.com/demux/django-sublime-scroll',
    description='Sublime Text 2 editor style scroll bars.',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development',
    ],
)