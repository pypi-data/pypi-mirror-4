from setuptools import setup, find_packages
import formalize
import sys, os

def readfile(path):
    f = open(path, 'r')
    try:
        return f.read()
    finally:
        f.close()

setup(
    name='formalize',
    version=readfile('VERSION.txt').strip(),
    description="Form processing and validation",
    long_description=readfile('README.txt') + readfile('CHANGELOG.txt'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='',
    author='Oliver Cope',
    author_email='oliver@redgecko.org',
    url='http://ollycope.com/software/formalize/',
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points="""
        # -*- Entry points: -*-
    """,
)
