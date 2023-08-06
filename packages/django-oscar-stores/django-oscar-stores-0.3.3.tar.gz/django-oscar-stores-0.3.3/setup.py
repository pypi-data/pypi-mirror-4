#!/usr/bin/env python
import os
from setuptools import setup, find_packages

setup(
    name='django-oscar-stores',
    version=":versiontools:stores:",
    url='https://github.com/tangentlabs/django-oscar-stores',
    author="Sebastian Vetter",
    author_email="sebastian.vetter@tangentsnowball.com.au",
    description="An extension for Oscar to include store locations",
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    keywords="django, oscar, e-commerce",
    license='BSD',
    platforms=['linux'],
    packages=find_packages(exclude=["sandbox*", "tests*"]),
    include_package_data=True,
    install_requires=[
        'django-oscar>=0.5-pre-alpha',
        'versiontools>=1.1.9',
        'requests>=1.1,<1.2',
    ],
    dependency_links=['https://github.com/tangentlabs/django-oscar/tarball/master#egg=django-oscar-0.5-pre-alpha'],
    # See http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
      'Environment :: Web Environment',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Operating System :: Unix',
      'Programming Language :: Python'
    ]
)
