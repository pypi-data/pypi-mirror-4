#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Pythonic XML Data Binding Package

NodeTree provides a clean, modern API for working with XML in Python.

Version 0.3 adds support for XML document parsing:

.. code:: pycon

    >>> import nodetree
    >>> d = nodetree.Document('<article><p>Pre <b>Bold</b> Post</p></article>')
    >>> d
    <?xml version="1.0"?>
    <article>
      <p>Pre <b>Bold</b> Post</p>
    </article>
    >>> str(d.root)
    '<?xml version="1.0"?>\\n<article><p>Pre <b>Bold</b> Post</p></article>\\n'
    >>> d.root[0]
    <p>Pre <b>Bold</b> Post</p>
    >>> d.root[0].pop()
    ' Post'
    >>> d.root[0][0] = 'Plain Text vs '
    >>> d.root
    <article>
      <p>Plain Text vs <b>Bold</b></p>
    </article>

XML streams (eg, XMPP) are also now supported with progressive parsing:

.. code:: pycon

    >>> import nodetree
    >>> s = nodetree.Stream('<stream:stream xmlns="jabber:client" ' +
                            'xmlns:stream="http://etherx.jabber.org/streams">')
    >>> s.send('<message><body>Hello, World!</body></message>')
    >>> s.root.pop(0)
    <message>
      <body>Hello, World!</body>
    </message>
    >>> s.send('<message><body>This works')
    >>> s.root.pop(0)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    ValueError: incomplete branch
    >>> s.send(' well</body></message>')
    >>> s.root.pop(0)
    <message>
      <body>This works well</body>
    </message>

This release also adds support for ``ProcessingInstruction`` nodes and fixes
several bugs regarding XML branch splicing and merging.

.. warning::

    NodeTree is still in early development; this release lacks several basic
    features and contains known bugs which may render it unsuitable for many
    applications. Notably, there is currently no access to XML namespaces from
    Python and no support for CDATA nodes, XPath, or XSLT.
'''

__credits__ = '''Copyright (C) 2010,2011,2012,2013 Arc Riley

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program; if not, see http://www.gnu.org/licenses
'''

__author__  = '\n'.join((
    'Arc Riley <arcriley@gmail.com>',
))

__version__ = '0.3'

import os
import sys
import subprocess
from distutils.core import setup
from distutils.extension import Extension
from distutils.cmd import Command
from distutils.command import build_py

# sphinx setup
from sphinx.setup_command import BuildDoc

# getoutput moved from commands to subprocess in Python 3
if sys.version_info[0] == 2 :
  from commands import getstatusoutput
else :
  from subprocess import getstatusoutput


def sources (sources_dir) :
    ''' This is a source list generator

    It scans a sources directory and returns every .c file it encounters.
    '''
    for name in os.listdir(sources_dir) :
        subdir = os.path.join(sources_dir, name)
        if os.path.isdir(subdir) :
            for source in os.listdir(subdir) :
                if os.path.splitext(source)[1] == '.c' :
                    yield os.path.join(subdir, source)
        else :
            if os.path.splitext(subdir)[1] == '.c' :
                yield subdir

    # close the generator
    return


# This uses pkg-config to pull Extension config based on packages needed
def pkgconfig(*pkglist, **kw):
    flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries'}
    pkgs = ' '.join(pkglist)
    status, output = getstatusoutput("pkg-config --libs --cflags %s" % pkgs)
    if status != 0 :
        raise OSError('Package(s) Not Found\n\n%s' % output)
    for token in output.split() :
        if token[:2] in flag_map :
            kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])
        else :
            kw.setdefault('extra_compile_args', []).append(token)
    return kw


if __name__ == '__main__' : setup(
    #
    ###########################################################################
    #
    # PyPI settings (for pypi.python.org)
    #
    name             = 'NodeTree',
    version          = __version__,
    description      = __doc__.splitlines()[0],
    long_description = '\n'.join(__doc__.splitlines()[2:]),
    maintainer       = 'Arc Riley',
    maintainer_email = 'arcriley@gmail.org',
    url              = 'http://www.nodetree.org/',
    download_url     = 'http://pypi.python.org/pypi/NodeTree/' + __version__,
    license          = '', # provided by classifier
    classifiers      = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Text Processing :: Markup :: XML',
    ],
    #
    ###########################################################################
    #
    # Extension settings
    #
    ext_modules = [Extension(
        name = 'nodetree',
        sources = [source for source in sources('src')],
        define_macros = [
            ('NODETREE_VERSION', '"%s"' % __version__),
        ],
        **pkgconfig('libxml-2.0', include_dirs=['include'])
    )],
	cmdclass = {'build_docs': BuildDoc},
	command_options={
		'build_docs': {
			'source_dir': ('setup.py', 'docs'),
			'build_dir': ('setup.py', os.path.join("build", "docs")),
			'project': ('setup.py', 'nodetree'),
			'version': ('setup.py', __version__),
			},
		},
    #
    ###########################################################################
)

