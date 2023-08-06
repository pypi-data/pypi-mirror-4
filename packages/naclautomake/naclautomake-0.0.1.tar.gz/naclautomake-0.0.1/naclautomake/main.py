'''
Created on 2013-2-9

@author: Alex
'''
from makefile import NaClMakefile
from setting import NaClSetting
from define import NaClDefine
from solution import NaClSolution

class NaClAutoMake(NaClMakefile):
    '''
AutoMake
    '''
    def __init__(self, solutionname, solutionpath, outputpath, naclsdkpath, chromepath, toolchains, maketypes):
        self.__setting__ = NaClSetting(solutionpath, outputpath, naclsdkpath, chromepath, toolchains, maketypes)
        self.__define__ = NaClDefine(self.__setting__)
        self.__solution__ = NaClSolution(solutionname, self.__setting__)

    @property
    def solution(self):
        return self.__solution__

    def mfLicense(self):
        # output the copyright information
        res = '\
# Copyright (c) 2013 Alex Chi. All rights reserved.\n\
# NaCl Automake is licensed under a Creative Commons Attribution 3.0 Unported License\n\
# that can be found in the LICENSE file.\n\
\n\
#\n\
# GNU Make based build file.  For details on GNU Make see:\n\
#   http://www.gnu.org/software/make/manual/make.html\n\
#\n'
        return res

    def mfAllDeclare(self):
        res = '# Declare all'
        res = '\n'.join([res, 'all:'])
        return res

    def mfAll(self):
        res = '# all'
        res = '\n'.join([res, 'all: $(ALL_TARGETS)'])
        return res

    def mfClean(self):
        res = '# Declare clean'
        res = '\n'.join([res, self.__solution__.mfClean()])
        return res

    def makefile(self):
        res = self.mfLicense()
        res = '\n'.join([res, self.__define__.makefile()])
        res = '\n'.join([res, ''])
        res = '\n'.join([res, self.mfAllDeclare()])
        res = '\n'.join([res, ''])
        res = '\n'.join([res, self.__solution__.makefile()])
        res = '\n'.join([res, ''])
        res = '\n'.join([res, self.mfAll()])
        res = '\n'.join([res, ''])
        res = '\n'.join([res, self.mfClean()])
        return res

    def write(self, makefilename):
        of = open(makefilename, 'w')
        of.write(self.makefile())
        of.close()