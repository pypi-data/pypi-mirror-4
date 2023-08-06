'''
Created on 2013-2-9

@author: Alex
'''
from common import EMakeType
from setting import NaClSetting
from makefile import NaClMakefile

class NaClDefine(NaClMakefile):
    '''
all defines
    '''
    def __init__(self, setting):
        # check the type of input
        if type(setting) != NaClSetting:
            raise Exception('Sorry, the argument must be NaClSetting instance!')
        self.__setting__ = setting

    @property
    def setting(self):
        return self.__setting__

    def mfDefine(self):
        res = '# Var defines'
        res = '\n'.join([res, 'OSNAME:=$(shell python $(NACL_SDK_ROOT)/tools/getos.py)'])
        return res

    def mfPath(self):
        res = '# Path defines'
        res = '\n'.join([res, 'THIS_MAKEFILE:=$(abspath $(lastword $(MAKEFILE_LIST)))'])
        res = '\n'.join([res, 'THIS_MAKEFILE_PATH:=$(abspath $(dir $(THIS_MAKEFILE)))'])
        res = '\n'.join([res, 'SOLUTION_PATH?=' + self.__setting__.solutionPath])
        res = '\n'.join([res, 'OUTPUT_PATH?=' + self.__setting__.outputPath])
        res = '\n'.join([res, 'CHROME_PATH?=' + self.__setting__.chromePath])
        res = '\n'.join([res, 'NACL_SDK_ROOT?=' + self.__setting__.naclsdkPath])
        res = '\n'.join([res, 'NACL_TOOLCHAIN_PATH:=$(abspath $(NACL_SDK_ROOT)/toolchain)'])
        return res

    def mfCommand(self):
        res = '# Command defines'
        res = '\n'.join([res, 'CREATENMF:=python $(NACL_SDK_ROOT)/tools/create_nmf.py'])
        res = '\n'.join([res, 'OSCOMMAND:=python $(NACL_SDK_ROOT)/tools/oshelpers.py'])
        res = '\n'.join([res, 'CP:=$(OSCOMMAND) cp'])
        res = '\n'.join([res, 'MKDIR:=$(OSCOMMAND) mkdir'])
        res = '\n'.join([res, 'MV:=$(OSCOMMAND) mv'])
        res = '\n'.join([res, 'RM:=$(OSCOMMAND) rm'])
        return res

    def mfDefault(self):
        res = '# Default defines'
        res = '\n'.join([res, 'NACL_WARNINGS:=-Wno-long-long -Wall -Wswitch-enum -Werror -pedantic'])
        return res

    def mfFlag(self):
        res = '# Flag defines'
        if EMakeType.DEBUG in self.__setting__.maketypes:
            res = '\n'.join([res, 'CXXFLAGS_DEBUG:=-g -O0'])
        if EMakeType.PROFILE in self.__setting__.maketypes:
            res = '\n'.join([res, 'CXXFLAGS_PROFILE:=-g -2 -msse -mfpmath=sse -ffast-math -fomit-frame-pointer'])
        if EMakeType.DEPLOY in self.__setting__.maketypes:
            res = '\n'.join([res, 'CXXFLAGS_DEPLOY:=-s -3 -msse -mfpmath=sse -ffast-math -fomit-frame-pointer'])
        return res

    def makefile(self):
        res = self.mfDefine()
        res = '\n'.join([res, ''])
        res = '\n'.join([res, self.mfPath()])
        res = '\n'.join([res, ''])
        res = '\n'.join([res, self.mfCommand()])
        res = '\n'.join([res, ''])
        res = '\n'.join([res, self.mfDefault()])
        res = '\n'.join([res, ''])
        res = '\n'.join([res, self.mfFlag()])
        return res