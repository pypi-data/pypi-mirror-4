#
# Copyright 2012 John Keyes
#
# http://jkeyes.mit-license.org/
#

from setuptools import find_packages
from setuptools import setup

setup(
    name="django-methodview",
    version='0.1.2',
    description="Class based HTTP method view",
    long_description=open('README').read(),
    author="John Keyes",
    author_email="john@keyes.ie",
    license="MIT License",
    url="http://github.com/jkeyes/django-methodview",
    keywords='django python http',
    classifiers=[],
    packages=find_packages(),
    include_package_data=True,
    install_requires=["Django"]
)
