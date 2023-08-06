'''
Created on 2013-2-7

@author: Alex Chi
'''
from common import EToolChain
from common import EMakeType
from common import EProjectType
from makefile import NaClMakefile
from project import NaClProject

class NaClSolution(NaClMakefile):
    '''
a solution that contain all projects
    '''

    def __init__(self, name, setting):
        self.__name__ = name
        self.__setting__ = setting
        self.__projects__ = {}

    @property
    def name(self):
        return self.__name__

    def newProject(self, name, projecttype = EProjectType.NEXE):
        self.__projects__[name] = NaClProject(name, projecttype)
        return self.__projects__[name]

    def depend(self, dependname, bedependname):
        if dependname not in self.__projects__ and bedependname not in self.__projects__:
            raise Exception('can\'t find the ' + dependname + ' or ' + bedependname + ' from projects')
        # TODO: need to check the relationship between dependname and bedependname
        self.__projects__[dependname].depends = [bedependname]
        self.__projects__[bedependname].bedepends = [dependname]

    def mfSolution(self):
        res = '# Solution: ' + self.__name__
        res = '\n'.join([res, self.__name__ + ':'])
        for key in self.__projects__:
            if len(self.__projects__[key].bedepends) <= 0:
                res = ' '.join([res, key])
        return res

    def mfOutputPathByToolChainAndMakeType(self, toolchain, maketype):
        res = toolchain + '/' + maketype + ': | ' + toolchain
        res = '\n'.join([res, '    $(MKDIR) ' + toolchain + '/' + maketype])
        return res

    def mfOutputPathByToolChain(self, toolchain):
        res = '# Rules for ' + toolchain + ' toolchain'
        res = '\n'.join([res, toolchain + ':'])
        res = '\n'.join([res, '    $(MKDIR) ' + toolchain])
        return res

    def mfOutputPath(self):
        res = '# output path'
        for toolchain in self.__setting__.toolchains:
            res = '\n'.join([res, self.mfOutputPathByToolChain(toolchain)])
            for maketype in self.__setting__.maketypes:
                res = '\n'.join([res, self.mfOutputPathByToolChainAndMakeType(toolchain, maketype)])
        return res

    def mfIncludeHeaderDependencyFiles(self):
        res = '# Include header dependency files.'
        for toolchain in self.__setting__.toolchains:
            for maketype in self.__setting__.maketypes:
                res = '\n'.join([res, '-include ' + toolchain + '/' + maketype + '/*.d'])
        return res

    def mfProjects(self):
        res = '# List all projects'
        for key in self.__projects__:
            res = '\n'.join([res, ''])
            res = '\n'.join([res, self.__projects__[key].makefile()])
        return res

    def mfClean(self):
        res = '.PHONY: clean'
        res = '\n'.join([res, 'clean:'])
        for toolchain in self.__setting__.toolchains:
            for maketype in self.__setting__.maketypes:
                res = '\n'.join([res, '    $(RM) -fr ' + toolchain + '/' + maketype])
            res = '\n'.join([res, '    $(RM) -fr ' + toolchain])
        return res

    def makefile(self):
        res = self.mfSolution()
        res = '\n'.join([res, ''])
        res = '\n'.join([res, self.mfOutputPath()])
        res = '\n'.join([res, ''])
        res = '\n'.join([res, self.mfIncludeHeaderDependencyFiles()])
        res = '\n'.join([res, ''])
        res = '\n'.join([res, self.mfProjects()])
        return res