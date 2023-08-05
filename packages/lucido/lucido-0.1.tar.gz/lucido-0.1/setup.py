#!/usr/bin/env python

from setuptools import setup

setup(
    name='lucido',
    version='0.1',
    description='An automatic sensitive data scrubber and restorer.',
    long_description=open('README.rst').read() + "\n\n" + open('HISTORY.rst').read(),
    author='Nick Sinopoli',
    author_email='nsinopoli@gmail.com',
    url='http://git.io/lucido',
    license='BSD',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2'
    ),
    install_requires=['PyYAML>=3.10'],
    packages=['lucido'],
    package_dir={'lucido': 'lucido'},
    package_data={'lucido': ['script/*']},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'luci = lucido.main:main',
        ],
    }
)
