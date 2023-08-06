'''
Created on 2013-2-7

@author: Alex Chi
'''

def Enum(**enums):
    '''
From: StackOverflow
Url: http://stackoverflow.com/questions/36932/whats-the-best-way-to-implement-an-enum-in-python
    '''
    return type('Enum', (), enums)

EToolChain = Enum(NEWLIB = 'newlib', GLIBC = 'glibc', ARM = 'arm', PNACL = 'pnacl')
EMakeType = Enum(DEBUG = 'debug', PROFILE = 'profile', DEPLOY = 'deploy')
EProjectType = Enum(SLIB = 'a', DLIB = 'so', NEXE = 'nexe')

def UniqueSet(aset):
    '''
remove repeated item in set
    '''
    return set(aset)

def UniqueList(alist):
    '''
remove repeated item in list
    '''
    return list(UniqueSet(alist))