#!/usr/bin/env python
import os

# Redefine build to configure and make shared lib

class cd:
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.cwd = os.getcwd()
        os.chdir(self.path)

    def __exit__(self, *args):
        os.chdir(self.cwd)

from distutils.command import build

baseBuild = build.build

class Build(build.build):
	def run(self):
		with cd("graphdat/lib/module_graphdat"):
			os.system("chmod u+x config.guess")
			os.system("chmod u+x config.sub")
			os.system("chmod u+x configure")
			os.system("chmod u+x depcomp")
			os.system("chmod u+x install-sh")
			os.system("chmod u+x ltmain.sh")
			os.system("chmod u+x missing")
			os.system("./configure")
			os.system("make")
			os.system("make install")
		baseBuild.run(self)
		
build.build = Build

# List source files in graphdat/lib

exclude_dirs = ['.git']
exclude_files = ['.gitignore']
package_files = []
for root, dirs, files in os.walk('graphdat/lib'):
	files[:] = [f for f in files if f not in exclude_files]
	dirs[:] = [d for d in dirs if d not in exclude_dirs]
	package_files += ['%s/%s' % (root[9:], file) for file in files]

from distutils.core import setup

setup(
	name='graphdat',
	version='1.2',
	description='Graphdat instrumentation module',
	long_description='Instrument WSGI applications to send performance data back to your graphs at graphdat.com',
	author='Alphashack',
	author_email='support@graphdat.com',
	url='http://www.graphdat.com',
	packages=['graphdat'],
	package_data={'graphdat': package_files},
)
