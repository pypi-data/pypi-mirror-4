##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import sys
import os
from os.path import join, dirname, isdir, normpath
from email import message_from_string

import shutil
import zc.recipe.egg
import zc.buildout.easy_install
import pkg_resources

try:
    from urllib2 import urlopen
except ImportError:
    # Py3 location changed.
    from urllib.request import urlopen

confPyTemplate = """
templates_path = ['%(templatesDir)s']
source_suffix = '.txt'
master_doc = '%(indexDoc)s'
project = '%(project)s'
copyright = '%(copyright)s'
version = '%(version)s'
release = '%(release)s'
today_fmt = '%%B %%d, %%Y'
pygments_style = 'sphinx'
html_style = 'default.css'
html_static_path = ['%(staticDir)s']
html_last_updated_fmt = '%%b %%d, %%Y'
extensions = %(extensions)r
"""

class ZopeOrgSetup(object):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        options['script'] = join(buildout['buildout']['bin-directory'],
                                 options.get('script', self.name))
        self.egg = zc.recipe.egg.Egg(self.buildout, self.name, self.options)

    def openfile(self, fn):
        try:
            f = open(fn)
        except IOError:
            f = urlopen(fn)
        return f

    def install(self):
        installed = []
        eggs, workingSet = self.egg.working_set()
        if 'doc-eggs' in self.options:
            eggs = self.options['doc-eggs'].split()
        docs = [workingSet.find(pkg_resources.Requirement.parse(spec))
                for spec in eggs]

        # Create parts directory for configuration files.
        installDir = join(
            self.buildout['buildout']['parts-directory'], self.name)
        if not isdir(installDir):
            os.mkdir(installDir)

        srcDirs = eval(self.options.get('src-dirs','{}'))

        projectsData = {}
        #for each egg listed as a buildout option, create a configuration space.
        for doc in docs:
            partDir = join(installDir, doc.project_name)
            if not isdir(partDir):
                os.mkdir(partDir)
            installed.append(partDir)

            recipeDir = dirname(__file__)

            #create static directory
            staticDir = join(partDir, '.static')
            if not isdir(staticDir):
                os.mkdir(staticDir)
            installed.append(staticDir)
            if 'default.css' not in self.options:
                shutil.copy(join(recipeDir,'default.css'),
                            join(staticDir, 'default.css'))
                installed.append(join(staticDir, 'default.css'))
            elif self.options['default.css']:
                f = self.openfile(self.options['default.css'])
                open(join(staticDir,'default.css'), 'w').write(f.read())
                installed.append(join(staticDir, 'default.css'))

            #create templates directory
            templatesDir = join(partDir, '.templates')
            if not isdir(templatesDir):
                os.mkdir(templatesDir)
            installed.append(templatesDir)
            if 'layout.html' not in self.options:
                shutil.copy(join(recipeDir,'layout.html'),
                            join(templatesDir, 'layout.html'))
                installed.append(join(templatesDir, 'layout.html'))
            elif self.options['layout.html']:
                f = self.openfile(self.options['layout.html'])
                open(join(templatesDir,'layout.html'), 'w').write(f.read())
                installed.append(join(templatesDir, 'layout.html'))

            metadata = dict(message_from_string('\n'.join(
                doc._get_metadata('PKG-INFO'))).items())

            #create conf.py
            confPyPath = join(partDir, 'conf.py')
            confPy = open(confPyPath, 'w')
            confPy.write(confPyTemplate % dict(
                project=metadata.get('Name', doc.project_name),
                copyright=metadata.get('Author', 'Zope Community'),
                version=metadata.get('Version', doc.version),
                release=metadata.get('Version', doc.version),
                staticDir=staticDir,
                templatesDir=templatesDir,
                indexDoc=self.options.get('index-doc','index'),
                extensions=self.options.get('extensions','').split()
                ))
            confPy.close()
            installed.append(confPyPath)

            buildDir = self.options.get('build-dir',
                                        join(partDir, 'build'))
            if not isdir(buildDir):
                os.mkdir(buildDir)

            buildDir = os.path.join(buildDir, doc.project_name)
            if not isdir(buildDir):
                os.mkdir(buildDir)

            srcDir = join(doc.location, srcDirs.get(doc.project_name,
                self.options.get('src-dir', doc.project_name.replace('.','/'))))
            # fix bad path on windows (e.g. //foo\bar)
            srcDir = normpath(srcDir)

            projectsData[doc.project_name] = ['-q','-c', partDir,
                                              srcDir, buildDir]

        installed.extend(zc.buildout.easy_install.scripts(
            [(self.options['script'],
              'z3c.recipe.sphinxdoc',
              'main'),
             ],
            workingSet,
            self.options['executable'],
            self.buildout['buildout']['bin-directory'],
            extra_paths=self.egg.extra_paths,
            arguments = "%r" % projectsData,
            ))

        return installed

    update = install


def main(projects):
    import sphinx
    for project, args in projects.items():
        print("building docs for", project, "---> sphinx-build", " ".join(args))
        sphinx.main(argv=sys.argv+args)

