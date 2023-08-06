"""
Copyright (C) 2013 Alex Chi (The MIT License)
Welcom to use nacl-automake.

Author: Alex Chi
Repo: https://bitbucket.org/alexchicn/nacl-automake
eMail: alex@alexchi.me
License: please read the LICENSE file in root directory
"""
from main import NaClAutoMake

__all__ = ['NaClAutoMake']
__version__ = '0.0.1'
__build__ = '20130124'
__author__ = 'Alex Chi <alex@alexchi.me>'
__license__ = 'Creative Commons Attribution 3.0 Unported License'

__all__ += ['CreateAutoMake']

def CreateAutoMake(solutionname, solutionpath, outputpath, naclsdkpath, chromepath, toolchains, maketypes):
    return NaClAutoMake(solutionname, solutionpath, outputpath, naclsdkpath, chromepath, toolchains, maketypes)