'''
Functions to generate network visualization output files from 
AdvanceSyn Model Specification file.

Date created: 18th February 2019

This file is part of AdvanceSyn Modeller, which is a part of 
AdvanceSyn ToolKit.

Copyright (c) 2018, AdvanceSyn Private Limited.

Licensed under the Apache License, Version 2.0 (the "License") for 
academic and not-for-profit use only; commercial and/or for profit 
use(s) is/are not licensed under the License and requires a 
separate commercial license from the copyright owner (AdvanceSyn 
Private Limited); you may not use this file except in compliance 
with the License. You may obtain a copy of the License at 
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

def extractReactions(specList):
    reactionList = []
    for spec in specList:
        for rxn_ID in spec['Reactions']:
            reaction = spec['Reactions'][rxn_ID]
            reactionList.append(reaction)
    return reactionList

def processReactions(reactionList):
    reactionList = [x.split('|')[0] for x in reactionList]
    reactionList = [x.strip() for x in reactionList]
    reactionList = [[x.split('->')[0], x.split('->')[1]] 
                    for x in reactionList]
    reactionList = [[x[0].split('+'), x[1].split('+')]
                    for x in reactionList] 
    reactionList = [[[s.strip() for s in x[0]], [d.strip() for d in x[1]]]
                    for x in reactionList]
    for index in range(len(reactionList)):
        if reactionList[index][0] == ['']:
            reactionList[index][0] = ['X']
        if reactionList[index][1] == ['']:
            reactionList[index][1] = ['X']
    return reactionList

def generateSIF(reactionList):
    datalist = []
    for index in range(len(reactionList)):
        sourceList = reactionList[index][0]
        substrate = 'r' + str(index) + 's'
        for s in sourceList:
            data = '%s cr %s' % (s, substrate)
            datalist.append(data)
        destinationList = reactionList[index][1]
        product = 'r' + str(index) + 'p'
        for d in destinationList:
            data = '%s rc %s' % (product, d)
            datalist.append(data)
        data = '%s rxn %s' % (substrate, product)
        datalist.append(data)
    return datalist

def generateNetworkMap(specList, outfmt):
    reactionList = extractReactions(specList)
    reactionList = processReactions(reactionList)
    if outfmt == 'SIF':
        datalist = generateSIF(reactionList)
    return datalist
