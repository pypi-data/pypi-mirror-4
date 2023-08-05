# Copyright (C) 2012 Bob Bowles <bobjohnbowles@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Work around mbcs bug in distutils. (for wininst)
# http://bugs.python.org/issue10945
import codecs
try:
    codecs.lookup('mbcs')
except LookupError:
    ascii = codecs.lookup('ascii')
    func = lambda name, enc = ascii: {True: enc}.get(name == 'mbcs')
    codecs.register(func)

from distutils.core import setup
import os

# locale root
targetLocaleRoot = ''
# TODO Windows stuff needs fixing
if os.name == 'nt': targetLocaleRoot = os.path.join('C:', 'Python32')
elif os.name == 'posix': targetLocaleRoot = os.path.join('/', 'usr', 'share')

# sort out the data files for the app
dataFiles = []

# sort out package data (e.g. gifs etc used in the app)
fileList = []
packageDir = 'src'
packageRoot = os.path.join(packageDir, 'UXBgtk')
dataRoot = 'images'
#for dir in os.listdir(os.path.join(packageRoot, dataRoot)):
#    path = os.path.join(packageRoot, dataRoot, dir)
#    if os.path.isdir(path):
for file in os.listdir(os.path.join(packageRoot, dataRoot)):
    fileList.append(os.path.join(dataRoot, file))

# add glade and css files, sort the results
fileList.append('UXBgtk.css')
fileList.append('UXBgtk.glade')
fileList.sort()

packageData = {'UXBgtk': fileList}

# detect Ubuntu/Unity to decide what to do with the launcher
from subprocess import Popen, PIPE
if os.name == 'posix':
    pipe = Popen('ps aux | grep unity', shell=True, stdout=PIPE).stdout

    # now scan the output for some unity tell-tale
    if  'unity-panel-service' in str(pipe.read()):
        print('Yay! Unity detected! Adding desktop launcher')
        dataFiles.append((os.path.join(targetLocaleRoot, 'applications'),
                          ['UXBgtk.desktop']))
    else:
        print('No Unity detected')
else:
     print('Not posix')

# now run setup
setup(
    name='UXBgtk',
    version='0.9',
    description='A Gtk version of the Mines game intended for casual play.',
    long_description=open('README.txt').read(),
    author='Bob Bowles',
    author_email='bobjohnbowles@gmail.com',
    url='http://pypi.python.org/pypi/UXBgtk/0.9',
    license='GNU General Public License v3 (GPLv3)', # TODO belt-n-braces??
    keywords=["Mines", ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux", # so far only tested on Linux
        "Topic :: Games/Entertainment :: Board Games",
        ],
    package_dir={'': packageDir},
    packages=['UXBgtk', ],
    requires=['gi (>=3.4.2)'], # TODO needs Python >3.3
    package_data=packageData,
    data_files=dataFiles,
)



