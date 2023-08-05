#!/usr/bin/env python
#coding:utf-8
from setuptools import setup, find_packages 

setup(
    name='42qucc',
    version="0.0.3",
    description= """
    A paste tool in CLI
        """,
    long_description="""
      the following is the usage:
      1.Paste file to 42qu.cc
        hi@Mars ~$ 42qucc < foo.txt            
        http://42qu.cc/xa47qt471        
      2.Custom url           
        hi@Mars ~$ 42qucc hi < foo.txt          
        http://42qu.cc/hi        
      3.Save web page to local file          
        hi@Mars ~$ 42qucc  http://42qu.cc/xa47qt471  >  foo.txt
        
      see more in http://42qu.cc/:help
    """,
    author="42qu.com 42区",
    author_email="admin@42qu.com",
    url="http://42qu.cc/:help",
    packages = [],
    zip_safe=False,
    include_package_data=True,
    install_requires = [
        'cc42>=0.0.2',
    ],

)

if __name__ == "__main__":
    import sys
    if sys.getdefaultencoding() == 'ascii':
        reload(sys)
        sys.setdefaultencoding('utf-8')

