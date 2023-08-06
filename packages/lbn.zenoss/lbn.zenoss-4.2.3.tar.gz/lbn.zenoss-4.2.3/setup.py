#
# Copyright 2010-2013 Corporation of Balclutha (http://www.balclutha.org)
# 
#                All Rights Reserved
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#


from setuptools import setup, find_packages

def read(name):
    try:
        return open(name).read()
    except:
	return ''


long_description=(
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
    )


setup(name='lbn.zenoss',
      version='4.2.3',
      description="Base wrappers to save real Zopistas from Zenoss cruft",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Plone",
        "Intended Audience :: Information Technology",
        "Programming Language :: Python",
        "Programming Language :: Zope",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Zope Public License",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking :: Monitoring",
        ],
      keywords='lbn zenoss',
      author='Alan Milligan',
      author_email='alan.milligan@last-bastion.net',
      url='http://au.last-bastion.net/zenoss',
      license='ZPL/2.1',
      packages=find_packages(),
      namespace_packages=['lbn',],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = zenoss
      """
)
