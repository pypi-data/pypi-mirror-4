#!/usr/bin/env python
"""
    Python "publish-subscribe" framework
    
    Created on 2012-01-19
    @author: Jean-Lou Dupont
"""
__author__  ="Jean-Lou Dupont"
__version__ ="0.2.0"


from distutils.core import setup
from setuptools import find_packages

DESC="""
Overview
--------

This package offers a "publish-subscribe" framework.

The framework can be used to implement basic "actors" where each "actor" is contained in a python module.
The function "upub" can be used to queue a message in front instead of the normal tail. 

Small Example
=============

::

    ## Actor 1 in module1.py
    ##
    from subpub import sub, pub
    
    @sub
    def on_topic1(param1):
        print "module1/topic1: ", param1

    @sub
    def on_topic2(param1):
        print "module1/topic2: ", param1
        

    ## Actor 2 in module2.py
    ##
    from subpub import sub, pub
    
    @sub
    def on_topic1(param1):
        print "module2/topic1: ", param1
        
    pub("topic1", "value1")
    pub("topic2", "value2")
    

The example above would yield:

::

    "module1/topic1: value1"
    "module2/topic1: value1"
    "module1/topic2: value2"
"""

setup(name=         'pysubpub',
      version=      __version__,
      description=  'Publish-Subscribe framework',
      author=       __author__,
      author_email= 'jl@jldupont.com',
      url=          'https://github.com/jldupont/pysubpub',
      package_dir=  {'': "src",},
      packages=     find_packages("src"),
      zip_safe=False
      ,install_requires=[
                         ]
      ,long_description=DESC
      ,classifiers=[
                    'Development Status :: 4 - Beta',
                    'Programming Language :: Python',
                    'Intended Audience :: Developers',
                    'Topic :: Utilities',
                    ]
      )

#############################################

f=open("latest", "w")
f.write(str(__version__)+"\n")
f.close()
