'''
Functions to generate ODE script from model objects.

Date created: 6th August 2018

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
import re
from datetime import datetime

def generate_object_table(objlist):
    '''!
    Function to generate a table of object numbering. from table 
    of objects.

    @param objlist Dictionary: Table of objects where key is the 
    object name and value is the object numbering.
    @return: Dictionary / table of objects where key is the object 
    name and value is the object numbering.
    '''
    objTable = {}
    count = 0
    for key in objlist:
        objTable[key] = count
        count = count + 1
    return objTable

def substitute_rateEq(objlist, objTable):
    '''!
    Function to change / edit each rate equations for each node / 
    entity to vector variable.

    @param objlist Dictionary: Table of objects where key is the 
    object name and value is the object numbering.
    @param objTable Dictionary: Table of objects where key is the 
    object name and value is the object numbering.
    @return: Modified table of objects.
    '''
    sTable = {}
    for k in objTable:
        sTable[k] = 'y[%s]' % str(objTable[k])
    for name in objlist: 
        for item in objlist[name].influx:
            for k in objTable:
                objlist[name].influx[item] = \
                    re.sub(r'\b%s\b' % k, sTable[k], 
                           objlist[name].influx[item])
        for item in objlist[name].outflux:
            for k in objTable:
                objlist[name].outflux[item] = \
                    re.sub(r'\b%s\b' % k, sTable[k], 
                           objlist[name].outflux[item])
    return objlist

def print_rateEq(objlist):
    '''!
    Function to generate the ODE function codes for each entity 
    from table of objects.

    @param objlist Dictionary: Table of objects where key is the 
    object name and value is the object numbering.
    @return: List of Python codes representing the ODE - one
    element is one line.
    '''
    printList = []
    for name in objlist:
        rateEq_name = re.sub('\.', '_', name)
        finalTerms = [[], []]
        pTerm = 'def %s(t, y):' % rateEq_name
        printList.append(pTerm)
        for item in objlist[name].influx:
            term = objlist[name].influx[item]
            termName = re.sub('\.', '_', item)
            pTerm = '    %s = %s' % (termName, term)
            printList.append(pTerm)
            finalTerms[0].append(termName)
        for item in objlist[name].outflux:
            term = objlist[name].outflux[item]
            termName = re.sub('\.', '_', item)
            pTerm = '    %s = %s' % (termName, term)
            printList.append(pTerm)
            finalTerms[1].append(termName)
        if len(finalTerms[0]) == 0: finalTerms[0] = ['0']
        if len(finalTerms[1]) == 0: finalTerms[1] = ['0']
        finalTerms = [' + '.join(finalTerms[0]), 
                      ' + '.join(finalTerms[1])]
        finalTerms = ['(%s)' % finalTerms[0],
                      ' - (%s)' % finalTerms[1]]
        finalTerms = ''.join(finalTerms)
        pTerm = '    return %s' % finalTerms
        printList.append(pTerm)
        printList.append(' ')
    return printList

def print_header(spec):
    '''!
    Function to generate / print the headers / comments for the 
    ODE script.

    @param spec Object: ConfigParser object containing the processed 
    model - from model_access.modelspec_reader() or 
    model_access.specobj_reader() functions.
    @return: List of Python codes representing the ODE - one
    element is one line.
    '''
    utcnow = datetime.utcnow()
    dtstamp = '%s-%s-%s %s:%s:%s:%s' % (str(utcnow.year), 
                                        str(utcnow.month), 
                                        str(utcnow.day), 
                                        str(utcnow.hour), 
                                        str(utcnow.minute), 
                                        str(utcnow.minute), 
                                        str(utcnow.microsecond))
    printList = ["''' -------------------------------------",
                 'Python ODE script generated by ASModeller',
                 '(a package in AdvanceSynToolKit)',
                 '',
                 'Date Time: %s' % dtstamp,
                 '']
    for key in spec['Identifiers']:
        printList.append('%s: %s' % (str(key), 
                         str(spec['Identifiers'][key])))
    printList.append("------------------------------------- '''")
    printList.append('')
    return printList

def print_Setup(objlist, objTable, solver='RK4', 
                timestep=1, endtime=21600,
                lowerbound=[0.0, 0.0], upperbound=[1e-3, 1e-3]):
    '''!
    Function to generate / print ODE simulation setup codes.

    @param objlist Dictionary: Table of objects where key is the 
    object name and value is the object numbering.
    @param objTable Dictionary: Table of objects where key is the 
    object name and value is the object numbering.
    @param solver String: Type of solver to use. Allowable types 
    are 'Euler', 'Heun' (Runge-Kutta 2nd method or Trapezoidal), 
    'RK3' (third order Runge-Kutta), 'RK4' (fourth order 
    Runge-Kutta), 'RK38' (fourth order Runge-Kutta method, 3/8 rule), 
    'CK4' (fourth order Cash-Karp), 'CK5' (fifth order Cash-Karp), 
    'RKF4' (fourth order Runge-Kutta-Fehlberg), 'RKF5' (fifth 
    order Runge-Kutta-Fehlberg), 'DP4' (fourth order Dormand-Prince), 
    and 'DP5' (fifth order Dormand-Prince). Default = 'RK4'.  
    @param timestep Float: Time step interval for simulation. 
    Default = 1.0.
    @param endtime Float: Time to end simulation - the simulation 
    will run from 0 to end time. Default = 21600.
    @param lowerbound String: Define lower boundary of objects. For 
    example, "[1, 2]" means that when the value of the object hits 1, 
    it will be bounced back to 2. Default = [0.0, 0.0]; that is, 
    when the value of the object goes to negative, it will be 
    bounced back to zero. 
    @param upperbound String: Define upper boundary of objects. For 
    example, "[10, 9]" means that when the value of the object hits 
    1, it will be pushed down to 9. Default = [1e-3, 1e-3]; that is, 
    when the value of the object above 1e-3, it will be pushed back 
    to 1e-3. 
    @return: List containing the Python ODE setup codes (one 
    element = one line).
    '''
    # 1. Generate ode codes
    odecode = [x[:-1] for x in open('ASModeller\\ode.py').readlines()]
    printList = odecode[8:37]
    if solver == 'Euler':
        printList = printList + odecode[37:115]
    if solver == 'Heun':
        printList = printList + odecode[115:204]
    if solver == 'RK3':
        printList = printList + odecode[204:303]
    if solver == 'RK4':
        printList = printList + odecode[303:409]
    if solver == 'RK38':
        printList = printList + odecode[409:515]
    if solver == 'CK4':
        printList = printList + odecode[515:641]
    if solver == 'CK5':
        printList = printList + odecode[641:766]
    if solver == 'RKF4':
        printList = printList + odecode[766:892]
    if solver == 'RKF5':
        printList = printList + odecode[892:1020]
    if solver == 'DP4':
        printList = printList + odecode[1020:1158]
    if solver == 'DP5':
        printList = printList + odecode[1158:1296]
    # 2. Generate ODE vector
    pTerm = 'ODE = list(range(%s))' % len(objTable)
    #print(pTerm)
    printList.append(pTerm)
    labels = ['time']
    for eqName in objTable:
        name = re.sub('\.', '_', eqName)
        pTerm = 'ODE[%s] = %s' % (str(objTable[eqName]), str(name))
        printList.append(pTerm)
        labels.append(name)
    printList.append(' ')
    # 3. Generate y vector
    pTerm = 'y = list(range(%s))' % len(objlist)
    printList.append(pTerm)
    for name in objTable:
        obj = objlist[name]
        pTerm = 'y[%s] = %s    # %s : %s' % \
            (str(objTable[name]), str(obj.value['initial']),
             str(name), str(obj.description))
        printList.append(pTerm)
    printList.append(' ')
    # 4. Print labels
    pTerm = 'labels = %s' % str(labels)
    printList.append(pTerm)
    printList.append(' ')
    # 5. Boundary conditions
    pTerm = 'lowerbound = {'
    for name in objTable:
        pTerm = pTerm + "'%s': [%s, %s], " % \
                        (str(objTable[name]), 
                         str(lowerbound[0]), 
                         str(lowerbound[1]))
    pTerm = pTerm + "}"
    printList.append(pTerm)
    printList.append(' ')
    pTerm = 'upperbound = {'
    for name in objTable:
        pTerm = pTerm + "'%s': [%s, %s], " % \
                        (str(objTable[name]), 
                         str(upperbound[0]), 
                         str(upperbound[1]))
    pTerm = pTerm + "}"
    printList.append(pTerm)
    printList.append(' ')
    # 6. Generate ODE execution
    pTerm = \
    'model = %s(ODE, 0.0, y, %s, %s, \
None, lowerbound, upperbound)' % \
        (str(solver), str(timestep), str(endtime))
    printList.append(pTerm)
    return printList

def generate_ODE(spec, modelobj, solver='RK4', 
                 timestep=1, endtime=21600, 
                 lowerbound='0;0', upperbound='1e-3;1e-3'):
    '''!
    Function to generate Python ODE codes by wrapping up other 
    generation functions.

    @param spec Object: ConfigParser object containing the processed 
    model - from model_access.modelspec_reader() or 
    model_access.specobj_reader() functions.
    @param modelobj Dictionary: Table of objects where key is the 
    object name and value is the object numbering.
    @param solver String: Type of solver to use. Allowable types 
    are 'Euler', 'Heun' (Runge-Kutta 2nd method or Trapezoidal), 
    'RK3' (third order Runge-Kutta), 'RK4' (fourth order 
    Runge-Kutta), 'RK38' (fourth order Runge-Kutta method, 3/8 rule), 
    'CK4' (fourth order Cash-Karp), 'CK5' (fifth order Cash-Karp), 
    'RKF4' (fourth order Runge-Kutta-Fehlberg), 'RKF5' (fifth 
    order Runge-Kutta-Fehlberg), 'DP4' (fourth order Dormand-Prince), 
    and 'DP5' (fifth order Dormand-Prince). Default = 'RK4'.  
    @param timestep Float: Time step interval for simulation. 
    Default = 1.0.
    @param endtime Float: Time to end simulation - the simulation 
    will run from 0 to end time. Default = 21600.
    @param lowerbound String: Define lower boundary of objects. For 
    example, "1,2" means that when the value of the object hits 1, 
    it will be bounced back to 2. Default = 0,0; that is, when the 
    value of the object goes to negative, it will be bounced back 
    to zero. 
    @param upperbound String: Define upper boundary of objects. For 
    example, "10,9" means that when the value of the object hits 1, 
    it will be pushed down to 9. Default = 1e-3,1e-3; that is, when 
    the value of the object above 1e-3, it will be pushed back to 
    1e-3. 
    @return: List containing the Python ODE codes (one element = 
    one line).
    '''
    objTable = generate_object_table(modelobj)
    modelobj = substitute_rateEq(modelobj, objTable)
    ODEHeader = print_header(spec)
    ODEList = print_rateEq(modelobj)
    lowerbound = [float(x) for x in lowerbound.strip().split(';')]
    upperbound = [float(x) for x in upperbound.strip().split(';')]
    ODESetup = print_Setup(modelobj, objTable, solver, 
                           timestep, endtime, 
                           lowerbound, upperbound)
    datalist = ODEHeader + ODEList + ODESetup
    return datalist
