#-*- coding:utf-8 -*-

from setuptools import setup
long_description = open("README.txt").read() + "\n\n" +  open("CHANGES.md").read() 

# hack, or test wont run on py2.7
try:
    import multiprocessing
    import logging
except:
    pass

setup(
    name='xmla',
    version='0.5',
    url="https://github.com/may-day/olap",
    license='Apache Software License 2.0',
    classifiers = [
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 2",
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules"
        ],
    description='Access olap data sources through xmla',
    long_description=long_description,
    author='Norman Krämer',
    author_email='kraemer.norman@googlemail.com',
    packages=['olap', 'olap.xmla'],
    namespace_packages=['olap'],
    package_dir={'olap':'olap', 'olap.xmla': 'olap/xmla'},
    package_data={'olap.xmla': ['vs.wsdl']},
    install_requires=[
      'olap',
      'suds',
      'kerberos',
      's4u2p',
      'requests'
    ],
   tests_require = [
        'nose',
    ],

    test_suite = 'nose.collector',

    include_package_data=True,
    zip_safe=False,
)
