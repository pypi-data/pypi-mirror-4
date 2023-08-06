# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys
sys.path.append('./sphinxcontrib')

f = open('README', 'r')
try:
    long_desc = f.read()
finally:
    f.close()
    
requires = ['Sphinx>=0.6']

setup(
    name='sphinxcontrib-smblink',
    version='0.2',
    author='Joey Chen',
    author_email='joey-tech@goingmyway.net',
    url='https://github.com/goingmywaynet/sphinxcontrib-smblink.git',
    description='Sphinx Windows Share Links (WSL) role extension',
    long_description=long_desc,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: Japanese',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    license='BSD',
    platforms='any',
    keywords = 'sphinx,sphinxcontrib,smb,windows,link,share',
    zip_safe=False,
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
    test_suite = "smblink_test.suite",
)
