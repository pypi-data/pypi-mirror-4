# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages
import chimere


try:
    reqs = open(os.path.join(os.path.dirname(__file__),
                             'requirements.txt')).read()
except (IOError, OSError):
    reqs = ''

setup(
    name='chimere',
    version=chimere.get_version(),
    description=
    "Chimere is a kind of online “mashup” which is designed to aggregate "\
    "geographic data from several sources. Chimere gets a map from "\
    "OpenStreetMap and display other data added by users. Datas are freely "\
    "submitted by visitors and then validated by an administrator.",
    long_description=open('README.txt').read(),
    author=u'Étienne Loks',
    author_email='etienne.loks@peacefrogs.net',
    url='http://blog.peacefrogs.net/nim/chimere/',
    license='GPL v3 licence, see COPYING',
    packages=find_packages(),
    include_package_data=True,
    install_requires=reqs,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
    ]
)
