'''
Created on 2013-2-9

@author: Alex
'''
from common import EToolChain
from common import EMakeType
from common import UniqueSet
from makefile import NaClMakefile

class NaClSetting(NaClMakefile):
    '''
    '''

    def __init__(self, solutionpath, outputpath, naclsdkpath = '', chromepath = '', toolchains = [EToolChain.NEWLIB], maketypes = [EMakeType.DEBUG]):
        self.__solutionPath__ = solutionpath
        self.__outputPath__ = outputpath
        self.__naclsdkPath__ = naclsdkpath
        self.__chromePath__ = chromepath
        self.__toolchains__ = UniqueSet(toolchains)
        self.__maketypes__ = UniqueSet(maketypes)

    @property
    def naclsdkPath(self):
        return self.__naclsdkPath__

    @property
    def chromePath(self):
        return self.__chromePath__

    @property
    def solutionPath(self):
        return self.__solutionPath__

    @property
    def outputPath(self):
        return self.__outputPath__

    @property
    def toolchains(self):
        return self.__toolchains__

    @property
    def maketypes(self):
        return self.__maketypes__
