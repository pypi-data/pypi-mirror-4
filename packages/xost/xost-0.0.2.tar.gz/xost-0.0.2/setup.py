#!/usr/bin/env python

from distutils.core import setup


setup(
    name='xost',
    version=__import__('xost').__version__,
    packages=['xost', 'xost.management', 'xost.management.commands'],
    url='',
    license='MIT',
    author='gratromv',
    #author_email='',
    description='Xost is a small embedded server which simplifies hosting of django applications',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python',
    ],
    install_requires=['django', 'Twisted',],
)
