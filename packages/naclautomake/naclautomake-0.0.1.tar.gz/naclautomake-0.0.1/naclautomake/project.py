'''
Created on 2013-2-7

@author: Alex Chi
'''
from common import EProjectType
from common import UniqueList
from makefile import NaClMakefile

class NaClProject(NaClMakefile):
    '''
a project that contain all code files
    '''

    def __init__(self, name, projecttype = EProjectType.NEXE):
        self.__name__ = name
        self.__type__ = projecttype
        self.__depends__ = []
        self.__bedepends__ = []

    @property
    def name(self):
        return self.__name__

    @property
    def type(self):
        return self.__type__

    @type.setter
    def type(self, value):
        self.__type__ = value

    @property
    def depends(self):
        return self.__depends__

    @depends.setter
    def depends(self, value):
        self.__depends__ += value
        self.__depends__ = UniqueList(self.__depends__)

    @property
    def bedepends(self):
        return self.__bedepends__

    @bedepends.setter
    def bedepends(self, value):
        self.__bedepends__ += value
        self.__bedepends__ = UniqueList(self.__bedepends__)

    def mfGenerateNMF(self):
        res = '# generate nmf file'
        res = '\n'.join([res, 'ALL_TARGETS+='])
        return res

    def makefile(self):
        res = '# Project: ' + self.__name__ + ' | Type: ' + self.__type__
        res = '\n'.join([res, self.__name__ + ':'])
        for dependname in self.__depends__:
            res = ' '.join([res, dependname])
        if self.__type__ == EProjectType.NEXE:
            res = '\n'.join([res, ''])
            res = '\n'.join([res, self.mfGenerateNMF()])
        return res