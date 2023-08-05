"""
Examples
========

No examples are implemented yet. Write to the author for more information.

"""

import math
import os.path
import pickle
import random
import time

import numpy as np

#from orngScaleData import getVariableValuesSorted
#from OWDistanceFile import readMatrix

from Orange import data, feature

from model import *
from modelmap import *

#ROOT = "/home/miha/work/res/metamining/"
#OUT_FILE = ROOT + "dst/zoo"
#OUT_FILE = ROOT + "dst/zoo"
#OUT_FILE = ROOT + "_astra_/fprdk"
#
#def saveSymMatrix(matrix, file, items=None, saveItems=False):
#    fn = open(file + ".dst", 'w')
#    fn.write("%d labeled\n" % matrix.dim)
#    items = items if items else matrix.items
#    for i in range(matrix.dim):
#        fn.write("%s" % items[i]['attributes'])
#        for j in range(i + 1):
#            fn.write("\t%.6f" % matrix[i, j])
#        fn.write("\n")
#
#    fn.close()
#    if saveItems:
#        items.save(file + ".tab")
#
#
#
#def loadModel(fn):
#    if os.path.exists('%s.npy' % fn):
#        matrix, _labels, data = readMatrix('%s.npy' % fn)
#    elif os.path.exists("%s-prob.dst" % fn):
#        matrix, _labels, data = readMatrix("%s-prob.dst" % fn)
#    elif os.path.exists("%s.dst" % fn):
#        matrix, _labels, data = readMatrix("%s.dst" % fn)
#    else:
#        return None
#
#    if os.path.exists("%s.tab" % fn):
#        data = data.Table("%s.tab" % fn)
#        matrix.items = data
#    else:
#        print "ExampleTable %s not found!\n" % ("%s.tab" % fn)
#    if os.path.exists("%s.res" % fn):
#        matrix.results = pickle.load(open("%s.res" % fn, 'rb'))
#    else:
#        print "Results pickle %s not found!\n" % ("%s.res" % fn)
#
#    return matrix
#
#def saveModel(smx, fn):
#    saveSymMatrix(smx, "%s" % fn, smx.items)
#    smx.items.save('%s.tab' % fn)
#    pickle.dump(smx.results, open('%s.res' % fn, "wb"))
#
#
#def evaluateProjections(vizr, attributeList):
#    vizr.evaluatedProjectionsCount = 0
#    vizr.optimizedProjectionsCount = 0
#    vizr.evaluationData = {}            # clear all previous data about tested permutations and stuff
#    vizr.evaluationData["triedCombinations"] = {}
#    vizr.clearResults()
#
#    vizr.clearArguments()
#
#    if vizr.projOptimizationMethod != 0:
#        vizr.freeviz.useGeneralizedEigenvectors = 1
#        vizr.graph.normalizeExamples = 0
#
#    domain = data.Domain([feature.Continuous("xVar"), feature.Continuous("yVar"), feature.Discrete(vizr.graph.dataDomain.classVar.name, values=getVariableValuesSorted(vizr.graph.dataDomain.classVar))])
#    classListFull = vizr.graph.originalData[vizr.graph.dataClassIndex]
#
#    for attributes in attributeList:
#        attrIndices = [vizr.graph.attributeNameIndex[attr] for attr in attributes]
#        #print attrIndices
#        if vizr.projOptimizationMethod != 0:
#            projections = vizr.freeviz.findProjection(vizr.projOptimizationMethod, attrIndices, setAnchors=0, percentDataUsed=vizr.percentDataUsed)
#            if projections != None:
#                xanchors, yanchors, (attrNames, newIndices) = projections
#                table = vizr.graph.createProjectionAsExampleTable(newIndices, domain=domain, XAnchors=xanchors, YAnchors=yanchors)
#
#            if table == None or len(table) < vizr.minNumOfExamples: continue
#            accuracy, other_results = vizr.evaluateProjection(table)
#            generalDict = {"XAnchors": list(xanchors), "YAnchors": list(yanchors), "Results": vizr.evaluationResults} if vizr.saveEvaluationResults else {"XAnchors": list(xanchors), "YAnchors": list(yanchors)}
#            vizr.addResult(accuracy, other_results, len(table), attrNames, vizr.evaluatedProjectionsCount, generalDict=generalDict)
#            vizr.evaluatedProjectionsCount += 1
#        else:
#            XAnchors = vizr.graph.createXAnchors(len(attrIndices))
#            YAnchors = vizr.graph.createYAnchors(len(attrIndices))
#            validData = vizr.graph.getValidList(attrIndices)
#            if numpy.sum(validData) >= vizr.minNumOfExamples:
#                classList = numpy.compress(validData, classListFull)
#                selectedData = numpy.compress(validData, numpy.take(vizr.graph.noJitteringScaledData, attrIndices, axis=0), axis=1)
#                sum_i = vizr.graph._getSum_i(selectedData)
#
#                table = vizr.graph.createProjectionAsExampleTable(attrIndices, validData=validData, classList=classList, sum_i=sum_i, XAnchors=XAnchors, YAnchors=YAnchors, domain=domain)
#                accuracy, other_results = vizr.evaluateProjection(table)
#                generalDict = {"Results": vizr.evaluationResults} if vizr.saveEvaluationResults else {}
#                vizr.addResult(accuracy, other_results, len(table), [vizr.graph.attributeNames[i] for i in attrIndices], vizr.evaluatedProjectionsCount, generalDict)
#                vizr.evaluatedProjectionsCount += 1
#
#    return vizr.evaluatedProjectionsCount
