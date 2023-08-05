# coding: utf-8
from setuptools import setup, find_packages
from distutils.core import  Extension
import commands

def pkgconfig(*packages, **kw):
    '''
    http://code.activestate.com/recipes/502261-python-distutils-pkg-config/
    '''
    flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries'}
    for token in commands.getoutput("pkg-config --libs --cflags %s" % ' '.join(packages)).split():
        if flag_map.has_key(token[:2]):
            kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])
        else: # throw others to extra_link_args
            kw.setdefault('extra_link_args', []).append(token)

    for k, v in kw.iteritems(): # remove duplicated
        kw[k] = list(set(v))

    return kw


ext_modules = [
    Extension("xmmsclient.xmmsvalue", ["xmmsvalue.c"], **pkgconfig('xmms2-client')),
    Extension("xmmsclient.xmmsapi", ["xmmsapi.c"], **pkgconfig('xmms2-client'))
]

setup(
  name = 'xmmsclient',
  summary='Xmms2 native client',
  version='0.8.1',
  license='LGPL',
  maintainer=u'Loïc Faure-Lacroix',
  maintainer_email='lamerstar@gmail.com',
  packages = find_packages(),
  home_page='http://xmms2.org/wiki/Main_Page',
  ext_modules = ext_modules
)
