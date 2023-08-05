# -*- encoding: utf-8 -*-
'''
Manage diglot filesytem from Akara configuration

Requires a configuration section, for example:

class diglot:
    rootPath       = '..'
    datasetName    = '..'
    graphUriFn     = functionName
    transforms4Dir = {
        u'.. FS directory ..' : u'.. FS XSLT path ..'
    }
'''

import akara
from akamu.diglot import Manager

def GetDiglotManager(graphUriFn):
    rootPath       = akara.module_config().get('rootPath')
    datasetName    = akara.module_config().get('datasetName')
    transforms4Dir = akara.module_config().get('transforms4Dir',{})
    return Manager(
        rootPath,
        datasetName,
        graphUriFn=graphUriFn,
        transforms4Dir=transforms4Dir)