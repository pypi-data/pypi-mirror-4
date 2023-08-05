#!/usr/bin/env python

from distutils.core import setup
import platform


if platform.system() == 'Linux':
    doc_dir = '/usr/share/doc/pyifbabel'
else:
    try:
        from win32com.shell import shellcon, shell
        homedir = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
        appdir = 'pyifbabel'
        doc_dir = os.path.join(homedir, appdir)
    except:
        pass


long_desc = \
"""pyifbabel is a libary and command-line tool for extracting metadata
information from interactive fiction (a.k.a. "text adventure") game files."""

setup(name='pyifbabel',
      version='0.2.3',
      description='A pure-Python implementation of the Treaty of Babel',
      long_description = long_desc,
      author='Brandon Invergo',
      author_email='brandon@invergo.net',
      url='http://grotesque.invergo.net/',
      packages=['treatyofbabel', 'treatyofbabel.formats', 'treatyofbabel.utils',
          'treatyofbabel.wrappers'],
      scripts=['pyifbabel'],
      data_files=[(doc_dir, ['COPYING', 'README', 'USAGE'])],
      classifiers=[
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Games/Entertainment'],
     )
