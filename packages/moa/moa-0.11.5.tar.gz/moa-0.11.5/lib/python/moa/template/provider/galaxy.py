# Copyright 2009-2011 Mark Fiers
# The New Zealand Institute for Plant & Food Research
# 
# This file is part of Moa - http://github.com/mfiers/Moa
# 
# Licensed under the GPL license (see 'COPYING')
# 
"""
moa.provider.core
-----------------

Provides templates from the Moa package.

"""
import os
import sys
import shutil

import Yaco

from xml.etree.ElementTree import ElementTree

import moa.utils
import moa.logger as l

from moa.sysConf import sysConf
from moa.template import provider


class Galaxy(provider.ProviderBase):

    def __init__(self, name, data):
        super(Galaxy, self).__init__(name, data)

    def hasTemplate(self, tName):
        #fname = os.path.join(self.directory, '%s.moa' % tName)
        return False #return os.path.isfile(fname)

    def getTemplate(self, name):
        """
        Returns a Yaco instance of the moa template
        """
        fname = os.path.join(self.directory, '%s.moa' % name)
        with open(fname) as F:
            data = F.read()
        return Yaco.Yaco(data)

    def templateList(self):
        """
        List all Moa package provided templates.

        @returns: a list of all templates included in the Moa package
        @rtype: a list of strings
        """
        r = []
        for conf in self.data.tool_config:
            tree = ElementTree()
            root = tree.parse(conf)
            if root.tag != 'tool':
                raise NotImplemented("other than very simple tools configuration files")
            r.append(root.get('name'))
        return r


    def installTemplate(self, wd, tName):
        """
        Install a template in the directory `wd`
        """
        moaFile = self.getTemplate(tName)
        extraFileDir = os.path.join(wd, '.moa', 'template.d')

        if os.path.isdir(extraFileDir):
            shutil.rmtree(extraFileDir)
        os.makedirs(extraFileDir)

        moaFile.save(os.path.join(wd, '.moa', 'template'))

        for f in os.listdir(self.directory):
            if not f.find(tName) == 0: continue
            if f[-1] in ['~', '#']: continue
            if f[-4:] == '.moa': continue
            shutil.copyfile(
                os.path.join(self.directory, f),
                os.path.join(wd, '.moa', 'template.d', f))

