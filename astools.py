'''
Command-line processor for AdvanceSyn ToolKit.

Date created: 6th August 2018

This file is a part of AdvanceSyn ToolKit.

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

import importlib
import os
import re
import sys
from pprint import pprint

import fire

import ASModeller

def printASM(modelfile, readertype):
    '''!
    Function to read the AdvanceSyn model specification file and 
    print out its details before processing into model objects.

    Usage:

        python astools.py printASM --modelfile=models/asm/glycolysis.modelspec --readertype=extended

    @param modelfile String: Relative path to the model specification 
    file.
    @param readertype String: Reader type for AdvanceSyn Model 
    spectification. Allowable types are 'basic' and 'extended'. 
    '''
    if readertype == 'basic':
        (spec, modelobj) = modelReader(modelfile, 'ASM', 'basic')
    elif readertype == 'extended':
        (spec, modelobj) = modelReader(modelfile, 'ASM', 'extended')
    else:
        print('readertype can only be basic or extended, %s given' \
            % readertype)
        return None
    for section in spec.sections():
        for item in spec[section]:
            print('%s/%s = %s' % (section, item, spec[section][item]))

def readASModelSpecification(modelfile):
    '''!
    Function to read the AdvanceSyn model specification file and 
    print out its details after processing into model objects.

    Usage:

        python astools.py readASM --modelfile=models/asm/glycolysis.modelspec

    @param modelfile String: Relative path to the model specification 
    file. This does not assume that the model file is in models folder.
    '''
    (spec, modelobj) = ASModeller.process_asm_model(modelfile)
    print('-------- Model Identifiers --------')
    for key in spec['Identifiers']:
        print('%s: %s' % (str(key), str(spec['Identifiers'][key])))
        print('')
    print('-------- Model Objects --------')
    for key in modelobj:
        obj = modelobj[key]
        print('Name: %s' % str(obj.name))
        print('Description: %s' % str(obj.description))
        print('Initial: %s' % str(obj.value['initial']))
        print('Influx:')
        pprint(obj.influx)
        print('Outflux:')
        pprint(obj.outflux)
        print('')

def fileWriter(datalist, relativefolder, filepath):
    '''!
    Function to write data from a list into a file.

    @param datalist List: Data to write into a file - one element per 
    line.
    @param relativefolder String: Relative folder to write the file 
    into.
    @param filepath String: Name of the file to be written into.
    '''
    filepath = relativefolder + '\\' + filepath
    filepath = os.path.abspath(filepath)
    odefile = open(filepath, 'w')
    for line in datalist:
        odefile.write(line + '\n')
    odefile.close()
    return filepath

def modelReader(modelfile, mtype, readertype='extended'):
    '''!
    Function to switch between different model specification readers 
    to read a given model specification into a dictionary of objects.

    @param modelfile String: Relative path to the model specification 
    file.
    @param mtype String: Type of model specification file. Allowable 
    types are 'ASM' (AdvanceSyn Model Specification). Default = 'ASM'.
    @param readertype String: Additional options based on mtype. If 
    mtype is ASM, then allowable types are 'basic' and 'extended'. 
    @return: A tuple of (Object containing the processed model, 
    Dictionary of objects where key is the object name and value is 
    the object numbering)
    '''
    if mtype == 'ASM':
        if readertype == 'extended': 
            (spec, modelobj) = ASModeller.process_asm_model(modelfile)
        if readertype == 'basic':
            spec = ASModeller.modelspec_reader(modelfile, 'basic')
            modelobj = None
    return (spec, modelobj)

def generateODEScript(modelfile, mtype='ASM', solver='RK4', 
                      timestep=1, endtime=21600,
                      odefile='odescript.py'):
    '''!
    Function to generate Python ODE script from a given model 
    specification file.

    Usage:

        python astools.py genODE --modelfile=asm/glycolysis.modelspec --mtype=ASM --solver=RK4 --timestep=1 --endtime=21600 --odefile=glycolysis.py

    @param modelfile String: Name of model specification file in 
    models folder. This assumes that the model file is in models 
    folder.
    @param mtype String: Type of model specification file. Allowable 
    types are 'ASM' (AdvanceSyn Model Specification). Default = 'ASM'.
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
    @param odefile String: Python ODE script file to write out. This 
    file will be written into odescript folder. Default = odescript.py.
    @return: A list containing the Python ODE script (one element = 
    one line).
    '''
    modelfile = 'models\\' + modelfile
    (spec, modelobj) = modelReader(modelfile, mtype, 'extended')
    datalist = ASModeller.generate_ODE(spec, modelobj, solver, 
                                       timestep, endtime)
    filepath = fileWriter(datalist, 'odescript', odefile)
    return datalist

def runODEScript(odefile, sampling=100, resultfile='oderesult.csv'):
    '''!
    Function to run / execute the ODE model and write out the 
    simulation results.

    Usage:

        python astools.py runODE --odefile=glycolysis.py --sampling=500 --resultfile=oderesult.csv

    @param odefile String: Python ODE script file (in odescript 
    folder) to run / execute.
    @param sampling Integer: Sampling frequency. If 100, means only 
    every 100th simulation result will be written out. The first 
    (start) and last (end) result will always be written out. 
    Default = 100.
    @param resultfile String: Relative or absolute file path to 
    write out simulation results. Default = 'oderesult.csv' 
    '''
    odefile = os.path.splitext(odefile)[0]
    m = importlib.import_module('odescript.'+ odefile)
    resultfile = os.path.abspath(resultfile)
    print('Executing ODE model - %s in odescript folder' % odefile)
    print('Sampling: %s' % str(int(sampling)))
    print('Output simulation result file: %s' % resultfile)
    resultfile = open(resultfile, 'w')
    resultfile.write(','.join(m.labels) + '\n')
    sampling = int(sampling)
    count = 0
    for data in m.model:
        if count % sampling == 0:
            data = [str(x) for x in data]
            resultfile.write(','.join(data) + '\n')
        count = count + 1
    data = [str(x) for x in data]
    resultfile.write(','.join(data) + '\n')
    resultfile.close()

def sensitivityGenerator(modelfile, multiple=100, 
                         prefix='', mtype='ASM'):
    '''!
    Function to generate a series of AdvanceSyn Model Specifications 
    from an existing model by multiplying a multiple to the variable 
    in preparation for sensitivity analyses.

    Usage:

        python astools.py senGen --modelfile=asm/glycolysis.modelspec --prefix=sen01 --mtype=ASM --multiple=100

    @param modelfile String: Name of model specification file in 
    models folder. This assumes that the model file is in models 
    folder.
    @param multiple Integer: Multiples to change each variable value. 
    Default = 100 (which will multiple the original parameter value 
    by 100).
    @param prefix String: A prefixing string for the set of new model 
    specification for identification purposes. Default = ''.
    @param mtype String: Type of model specification file. Allowable 
    types are 'ASM' (AdvanceSyn Model Specification). Default = 'ASM'.
    @return: Dictionary of file paths of generated models.
    '''
    gModelSpecFiles = {}
    # Step 1: Process baseline model
    # Step 1.1: Process original model file 
    (bspec, modelobj) = modelReader('models\\' + modelfile, 
                                    mtype, 'basic')
    spec = ASModeller.specobj_reader(bspec, 'extended')
    # Step 1.2: Process file path for original model
    if len(modelfile.split(os.sep)) == 1:
        filepath = modelfile.split('/')[-1]
    else:
        filepath = modelfile.split(os.sep)[-1]
    filepath = os.path.splitext(filepath)[0]
    if prefix == '':
        filepath = os.sep.join(['models', 'temp', 
            '%s.original.modelspec' % filepath])
    else:
        filepath = os.sep.join(['models', 'temp', 
            '%s.%s.original.modelspec' % (prefix, filepath)])
    # Step 1.3: Write out original model
    filepath = os.path.abspath(filepath)
    tModelFile = open(filepath, 'w')
    spec.write(tModelFile)
    tModelFile.close()
    # Step 1.4: Update file listings
    gModelSpecFiles['original'] = \
        {'ASM': os.path.abspath(filepath),
         'Change': 'None'}
    # Step 2: Generate models for changed parameter value 
    for param in bspec['Variables']:
        # Step 2.1: Change parameter value 
        original_parameter = float(bspec['Variables'][param])
        new_parameter = str(original_parameter * multiple)
        bspec.set('Variables', param, new_parameter)
        # Step 2.2: Reprocess model to update model
        spec = ASModeller.specobj_reader(bspec, 'extended')
        # Step 2.3: Process file path for new model
        if len(modelfile.split(os.sep)) == 1:
            filepath = modelfile.split('/')[-1]
        else:
            filepath = modelfile.split(os.sep)[-1]
        filepath = os.path.splitext(filepath)[0]
        if prefix == '':
            filepath = os.sep.join(['models', 'temp', 
                '%s.%s.modelspec' % (filepath, param)])
        else:
            filepath = os.sep.join(['models', 'temp', 
                '%s.%s.%s.modelspec' % (prefix, filepath, param)])
        # Step 2.4: Write out as new model
        filepath = os.path.abspath(filepath)
        tModelFile = open(filepath, 'w')
        spec.write(tModelFile)
        tModelFile.close()
        # Step 2.5: Update file listings
        gModelSpecFiles[param] = \
            {'ASM': os.path.abspath(filepath),
             'Change': '%s --> %s' % (str(original_parameter), 
                                      str(new_parameter))}
        print('Modified %s: %s --> %s' % \
            (param, str(original_parameter), str(new_parameter)))
        print('  New ASM model in %s' % str(filepath))
        # Step 2.6: Change back to original parameter value
        bspec.set('Variables', param, str(original_parameter))
    return gModelSpecFiles

def localSensitivity(modelfile, multiple=100, prefix='', 
                     mtype='ASM', solver='RK4', timestep=1, 
                     endtime=21600, cleanup=True,
                     resultfile='sensitivity_analysis.csv'):
    '''!
    Function to perform local sensitivity analysis using OFAT/OAT 
    (one factor at a time) method where the last data time (end 
    time) simulation results are recorded into results file.

    Usage:

        python astools.py LSA --modelfile=asm/glycolysis.modelspec --prefix=sen01 --mtype=ASM --multiple=100 --solver=RK4 --timestep=1 --endtime=21600 --cleanup=True --resultfile=sensitivity_analysis.csv

    @param modelfile String: Name of model specification file in 
    models folder. This assumes that the model file is in models 
    folder.
    @param multiple Integer: Multiples to change each variable value. 
    Default = 100 (which will multiple the original parameter value 
    by 100).
    @param prefix String: A prefixing string for the set of new model 
    specification for identification purposes. Default = ''.
    @param mtype String: Type of model specification file. Allowable 
    types are 'ASM' (AdvanceSyn Model Specification). Default = 'ASM'.
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
    @param cleanup String: Flag to determine whether to remove all 
    generated temporary models and ODE code files. Default = True.
    @param resultfile String: Relative or absolute file path to 
    write out sensitivity results. Default = 'sensitivity_analysis.csv'
    '''
    MSF = sensitivityGenerator(modelfile, multiple, prefix, mtype)
    for param in MSF:
        # Generate ODE codes from model
        (spec, modelobj) = modelReader(MSF[param]['ASM'], 
                                    mtype, 'extended')
        print('Processing model: %s' % MSF[param]['ASM'])
        ODECode = ASModeller.generate_ODE(spec, modelobj, solver, 
                 timestep, endtime)
        odefile = re.sub('\.', '_', param)
        filepath = fileWriter(ODECode, 'models/temp', odefile + '.py')
        MSF[param]['ODE'] = filepath
        # Simulate ODE codes
        m = importlib.import_module('models.temp.'+ odefile)
        labels = [param, 'Change'] + m.labels
        for data in m.model:
            simData = [str(x) for x in data]
        MSF[param]['Data'] = simData
    resultfile = os.path.abspath(resultfile)
    resultfile = open(resultfile, 'w')
    resultfile.write(','.join(labels) + '\n')
    for param in MSF:
        data = [param, MSF[param]['Change']] + MSF[param]['Data']
        data = [str(x) for x in data]
        resultfile.write(','.join(data) + '\n')
    resultfile.close()
    if str(cleanup).upper() == 'TRUE':
        for param in MSF:
            ASMfile = MSF[param]['ASM']
            ODEfile = MSF[param]['ODE']
            os.remove(ASMfile)
            os.remove(ODEfile)

if __name__ == '__main__':
    exposed_functions = {'printASM': printASM,
                         'readASM': readASModelSpecification,
                         'genODE': generateODEScript,
                         'LSA': localSensitivity,
                         'runODE': runODEScript,
                         'senGen': sensitivityGenerator}
    fire.Fire(exposed_functions)
