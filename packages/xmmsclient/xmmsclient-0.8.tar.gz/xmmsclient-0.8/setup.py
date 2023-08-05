# coding: utf-8
from setuptools import setup, find_packages
from distutils.core import  Extension

ext_modules = [
    Extension("xmmsclient.xmmsvalue", ["xmmsvalue.c"], 
        include_dirs=['/usr/local/include/xmms2'], libraries=['xmmsclient']),
    Extension("xmmsclient.xmmsapi", ["xmmsapi.c"], 
        include_dirs=['/usr/local/include/xmms2'], libraries=['xmmsclient']),
]

setup(
  name = 'xmmsclient',
  summary='Xmms2 native client',
  version='0.8',
  license='LGPL',
  maintainer=u'Loïc Faure-Lacroix',
  maintainer_email='lamerstar@gmail.com',
  packages = find_packages(),
  home_page='http://xmms2.org/wiki/Main_Page',
  ext_modules = ext_modules
)
