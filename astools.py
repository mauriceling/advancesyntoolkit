'''
Command-line processor for AdvanceSyn ToolKit.

Date created: 6th August 2018

Authors: Maurice HT Ling

This file is part of AdvanceSynModeller, which is a part of AdvanceSynToolKit.

Copyright (c) 2018, AdvanceSyn Private Limited and authors.

Reference: Ling, MHT. 2020. AdvanceSyn Toolkit: An Open-Source Suite for Model Development and Analysis in Biological Engineering. MOJ Proteomics & Bioinformatics 9(4):83‒86.


Licensed under the Apache License, Version 2.0 (the "License") for academic and not-for-profit use only; commercial and/or for profit use(s) is/are not licensed under the License and requires a separate commercial license from the copyright owner (AdvanceSyn Private Limited); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
'''
import argparse
import importlib
import inspect
import pickle
import os
import re
import subprocess
import sys
from pprint import pprint

import ASExternalTools
import ASModeller

def printASM(modelfile, readertype):
    '''!
    Function to read the AdvanceSyn model specification file and print out its details before processing into model objects.

    Usage:

        python astools.py printASM --modelfile=models/asm/glycolysis.modelspec --readertype=extended

    @param modelfile String: Relative path to the model specification file.
    @param readertype String: Reader type for AdvanceSyn Model spectification. Allowable types are 'basic' and 'extended'. 
    '''
    modelfile = os.path.abspath(modelfile)
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

def _printASModelSpecification(spec, modelobj):
    '''!
    Private method - To print out model details.

    @param spec Object: ConfigParser object containing the processed model
    @param modelobj Dictionary: Dictionary of objects where key is the object name and value is the object numbering.
    '''
    if spec != None:
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

def readModel(modelfile, mtype='ASM'):
    '''!
    Function to read a model file and print out its details after processing into model objects.

    Usage:

        python astools.py readmodel --mtype=ASM --modelfile=models/asm/glycolysis.modelspec

    @param modelfile String: Relative path to the model specification file. 
    @param mtype String: Type of model specification file. Allowable types are 'ASM' (AdvanceSyn Model Specification), 'MO' (AdvanceSyn Model Objects). Default = 'ASM'.
    '''
    modelfile = os.path.abspath(modelfile)
    (spec, modelobj) = modelReader(modelfile, mtype, 'extended')
    _printASModelSpecification(spec, modelobj)

def _printFluxes(modelobj):
    '''!
    Private method - To print out fluxes (productions and usages) of model objects.

    @param modelobj Dictionary: Dictionary of objects where key is the object name and value is the object numbering.
    '''
    results = []
    for key in modelobj:
        obj = modelobj[key]
        productions = '; '.join([str(k) for k in obj.influx])
        usages = '; '.join([str(k) for k in obj.outflux])
        if len(productions) == 0: productions = "NIL"
        if len(usages) == 0: usages = "NIL"
        results.append([str(obj.name), productions, usages])
    print('|'.join(['Name', 'Productions', 'Usages']))
    for obj in results:
        print('|'.join(obj))

def readFluxes(modelfile, mtype='ASM'):
    '''!
    Function to read the AdvanceSyn model objects file and print out fluxes (productions and usages) of model objects.

    Usage:

        python astools.py readflux --mtype=ASM --modelfile=models/asm/glycolysis.modelspec

    @param modelfile String: Relative path to the model object file. 
    @param mtype String: Type of model specification file. Allowable types are 'ASM' (AdvanceSyn Model Specification), 'MO' (AdvanceSyn Model Objects). Default = 'ASM'.
    '''
    modelfile = os.path.abspath(modelfile)
    (spec, modelobj) = modelReader(modelfile, mtype, 'extended')
    _printFluxes(modelobj)

def generateModelObject(modelfile, outputfile, prefix='exp'):
    '''!
    Function to read the AdvanceSyn model specification file(s) and generate a file consisting of the internal model objects.

    Usage:

        python astools.py genMO --prefix=exp --modelfile=models/asm/glycolysis.modelspec;models/asm/RFPproduction.modelspec --outputfile=models/mo/glycolysis.mo

    @param modelfile String: Relative path(s) to the model specification file(s), separated by semi-colon. 
    @param outputfile String: Relative path to the output model objects file.
    @param prefix String: Prefix for new reaction IDs. This prefix cannot be any existing prefixes in any of the model specifications to be merged. Default = 'exp'.
    '''
    specList = []
    modelobjList = []
    modelfile = [x.strip() for x in modelfile.split(';')]
    print('Input Model File(s) ...')
    count = 1
    for mf in modelfile:
        mf = os.path.abspath(mf)
        print('ASM Model File %s: %s' % (count, mf))
        (spec, modelobj) = modelReader(mf, 'ASM', 'extended')
        specList.append(spec)
        modelobjList.append(modelobj)
        count = count + 1
    print('')
    (merged_spec, merged_modelobj) = \
        ASModeller.modelMerge(specList, modelobjList, prefix, 
                              True, True)
    filepath = os.path.abspath(outputfile)
    print('Output Model Objects File: ' + filepath)
    with open(filepath, 'wb') as f:
        dumpdata = (merged_spec, merged_modelobj)
        pickle.dump(dumpdata, f, pickle.HIGHEST_PROTOCOL)

def mergeASM(modelfile, outputfile, prefix='exp'):
    '''!
    Function to read the AdvanceSyn model specification file(s) and merge them into a single AdvanceSyn model specification file.

    Usage:

        python astools.py mergeASM --prefix=exp --modelfile=models/asm/glycolysis.modelspec;models/asm/ppp.modelspec --outputfile=models/asm/glycolysis_ppp.modelspec

    @param modelfile String: Relative path(s) to the model specification file(s), separated by semi-colon. 
    @param outputfile String: Relative path to the output ASM model file.
    @param prefix String: Prefix for new reaction IDs. This prefix cannot be any existing prefixes in any of the model specifications to be merged. Default = 'exp'.
    '''
    specList = []
    modelobjList = []
    modelfile = [x.strip() for x in modelfile.split(';')]
    print('Input Model File(s) ...')
    count = 1
    for mf in modelfile:
        mf = os.path.abspath(mf)
        print('ASM Model File %s: %s' % (count, mf))
        (spec, modelobj) = modelReader(mf, 'ASM', 'basic')
        specList.append(spec)
        modelobjList.append(modelobj)
        count = count + 1
    print('')
    (merged_spec, merged_modelobj) = \
        ASModeller.modelMerge(specList, modelobjList, prefix, 
                              True, False)
    filepath = os.path.abspath(outputfile)
    print('Output AdvanceSyn Model Specification File: ' + filepath)
    outfile = open(filepath, 'w')
    merged_spec.write(outfile)
    outfile.close()

def generateNetwork(modelfile, outputfile, outfmt='SIF'):
    '''!
    Function to read the AdvanceSyn model specification file(s) and generate a network / reaction visualization file.

    Usage:

        python astools.py genNetwork --outfmt=SIF --modelfile=models/asm/glycolysis.modelspec;models/asm/ppp.modelspec --outputfile=glycolysis_ppp.sif

    @param modelfile String: Relative path(s) to the model specification file(s), separated by semi-colon. 
    @param outputfile String: Relative path to the output file.
    @param outfmt String: Type of network visualizatio format to generate. Allowable options are 'SIF' (Simple Interaction Format). Default = 'SIF' (Simple Interaction Format).
    '''
    specList = []
    modelfile = [x.strip() for x in modelfile.split(';')]
    print('Input Model File(s) ...')
    count = 1
    for mf in modelfile:
        mf = os.path.abspath(mf)
        print('ASM Model File %s: %s' % (count, mf))
        (spec, modelobj) = modelReader(mf, 'ASM', 'extended')
        specList.append(spec)
        count = count + 1
    print('')
    outfmt = str(outfmt).upper()
    datalist = ASModeller.generateNetworkMap(specList, outfmt)
    outputfile = os.path.abspath(outputfile)
    outfile = open(outputfile, 'w')
    print('Output File: ' + outputfile)
    print('Output Format: ' + outfmt)
    for line in datalist:
        outfile.write(str(line) + '\n')
    outfile.close()

def fileWriter(datalist, relativefolder, filepath):
    '''!
    Function to write data from a list into a file.

    @param datalist List: Data to write into a file - one element per line.
    @param relativefolder String: Relative folder to write the file into.
    @param filepath String: Name of the file to be written into.
    '''
    filepath = relativefolder + os.sep + filepath
    filepath = os.path.abspath(filepath)
    odefile = open(filepath, 'w')
    for line in datalist:
        odefile.write(line + '\n')
    odefile.close()
    return filepath

def modelReader(modelfile, mtype, readertype='extended'):
    '''!
    Function to switch between different model specification readers to read a given model specification into a dictionary of objects.

    @param modelfile String: Relative path to the model specification file.
    @param mtype String: Type of model specification file. Allowable types are 'ASM' (AdvanceSyn Model Specification). Default = 'ASM'.
    @param readertype String: Additional options based on mtype. If mtype is ASM, then allowable types are 'basic' and 'extended'. 
    @return: A tuple of (Object containing the processed model, Dictionary of objects where key is the object name and value is the object numbering)
    '''
    if mtype == 'ASM':
        if readertype == 'extended': 
            (spec, modelobj) = ASModeller.process_asm_model(modelfile)
        if readertype == 'basic':
            spec = ASModeller.modelspec_reader(modelfile, 'basic')
            modelobj = None
    if mtype == 'MO':
        with open(modelfile, 'rb') as f:
            loaded_data = pickle.load(f)
        spec = loaded_data[0]
        modelobj = loaded_data[1]
    return (spec, modelobj)

def generateODEScript(modelfile, mtype='ASM', solver='RK4', 
                      timestep=1, endtime=21600, 
                      lowerbound='0;0', 
                      upperbound='1e-3;1e-3',
                      odefile='odescript.py'):
    '''!
    Function to generate Python ODE script from a given model specification file.

    Usage:

        python astools.py genODE --modelfile=models/asm/glycolysis.modelspec --mtype=ASM --solver=RK4 --timestep=1 --endtime=21600 --lowerbound=0;0 --upperbound=1e-3;1e-3 --odefile=glycolysis.py

    @param modelfile String: Name of model specification file in models folder. This assumes that the model file is not in models folder.
    @param mtype String: Type of model specification file. Allowable types are 'ASM' (AdvanceSyn Model Specification). Default = 'ASM'.
    @param solver String: Type of solver to use. Allowable types are 'Euler', 'Heun' (Runge-Kutta 2nd method or Trapezoidal), 'RK3' (third order Runge-Kutta), 'RK4' (fourth order Runge-Kutta), 'RK38' (fourth order Runge-Kutta method, 3/8 rule), 'CK4' (fourth order Cash-Karp), 'CK5' (fifth order Cash-Karp),'RKF4' (fourth order Runge-Kutta-Fehlberg), 'RKF5' (fifth order Runge-Kutta-Fehlberg), 'DP4' (fourth order Dormand-Prince), and 'DP5' (fifth order Dormand-Prince). Default = 'RK4'. 
    @param timestep Float: Time step interval for simulation. Default = 1.0.
    @param endtime Float: Time to end simulation - the simulation will run from 0 to end time. Default = 21600.
    @param lowerbound String: Define lower boundary of objects. For example, "1;2" means that when the value of the object hits 1, it will be bounced back to 2. Default = 0;0; that is, when the value of the object goes to negative, it will be bounced back to zero. 
    @param upperbound String: Define upper boundary of objects. For example, "10;9" means that when the value of the object hits 1, it will be pushed down to 9. Default = 1e-3;1e-3; that is, when the value of the object above 1e-3, it will be pushed back to 1e-3. 
    @param odefile String: Python ODE script file to write out. This file will be written into odescript folder. Default = odescript.py.
    @return: A list containing the Python ODE script (one element = one line).
    '''
    modelfile = os.path.abspath(modelfile)
    (spec, modelobj) = modelReader(modelfile, mtype, 'extended')
    datalist = ASModeller.generate_ODE(spec, modelobj, solver, 
                                       timestep, endtime,
                                       lowerbound, upperbound)
    filepath = fileWriter(datalist, 'odescript', odefile)
    return datalist

def runODEScript(odefile, sampling=100, resultfile='oderesult.csv'):
    '''!
    Function to run / execute the ODE model and write out the simulation results.

    Usage:

        python astools.py runODE --odefile=glycolysis.py --sampling=500 --resultfile=oderesult.csv

    @param odefile String: Python ODE script file (in odescript folder) to run / execute.
    @param sampling Integer: Sampling frequency. If 100, means only every 100th simulation result will be written out. The first (start) and last (end) result will always be written out. Default = 100.
    @param resultfile String: Relative or absolute file path to write out simulation results. Default = 'oderesult.csv' 
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
            print("Time step = %s" % str(count))
        count = count + 1
    data = [str(x) for x in data]
    resultfile.write(','.join(data) + '\n')
    resultfile.close()

def sensitivityGenerator(modelfile, multiple=100, 
                         prefix='', mtype='ASM'):
    '''!
    Function to generate a series of AdvanceSyn Model Specifications from an existing model by multiplying a multiple to the variable in preparation for sensitivity analyses.

    Usage:

        python astools.py senGen --modelfile=models/asm/glycolysis.modelspec --prefix=sen01 --mtype=ASM --multiple=100

    @param modelfile String: Name of model specification file in models folder. This assumes that the model file is not in models folder.
    @param multiple Integer: Multiples to change each variable value. Default = 100 (which will multiple the original parameter value by 100).
    @param prefix String: A prefixing string for the set of new model specification for identification purposes. Default = ''.
    @param mtype String: Type of model specification file. Allowable types are 'ASM' (AdvanceSyn Model Specification). Default = 'ASM'.
    @return: Dictionary of file paths of generated models.
    '''
    gModelSpecFiles = {}
    # Step 1: Process baseline model
    # Step 1.1: Process original model file 
    (bspec, modelobj) = modelReader(modelfile, mtype, 'basic')
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
                     outfmt='reduced', sampling=100,
                     resultfile='sensitivity_analysis.csv'):
    '''!
    Function to perform local sensitivity analysis using OFAT/OAT (one factor at a time) method where the last data time (end time) simulation results are recorded into results file.

    Usage:

        python astools.py LSA --modelfile=models/asm/glycolysis.modelspec --prefix=sen01 --mtype=ASM --multiple=100 --solver=RK4 --timestep=1 --endtime=21600 --cleanup=True --outfmt=reduced --resultfile=sensitivity_analysis.csv

    @param modelfile String: Name of model specification file in models folder. This assumes that the model file is not in models folder.
    @param multiple Integer: Multiples to change each variable value. Default = 100 (which will multiple the original parameter value by 100).
    @param prefix String: A prefixing string for the set of new model specification for identification purposes. Default = ''.
    @param mtype String: Type of model specification file. Allowable types are 'ASM' (AdvanceSyn Model Specification). Default = 'ASM'.
    @param solver String: Type of solver to use. Allowable types are 'Euler', 'Heun' (Runge-Kutta 2nd method or Trapezoidal), 'RK3' (third order Runge-Kutta), 'RK4' (fourth order Runge-Kutta), 'RK38' (fourth order Runge-Kutta method, 3/8 rule), 'CK4' (fourth order Cash-Karp), 'CK5' (fifth order Cash-Karp), 'RKF4' (fourth order Runge-Kutta-Fehlberg), 'RKF5' (fifth order Runge-Kutta-Fehlberg), 'DP4' (fourth order Dormand-Prince), and 'DP5' (fifth order Dormand-Prince). Default = 'RK4'. 
    @param timestep Float: Time step interval for simulation. Default = 1.0.
    @param endtime Float: Time to end simulation - the simulation will run from 0 to end time. Default = 21600.
    @param cleanup String: Flag to determine whether to remove all generated temporary models and ODE code files. Default = True.
    @param outfmt String: Output format. Allowable types are 'reduced' (only the final result will be saved into resultfile) and 'full' (all data, depending on sampling, will be saved into resultfile).
    @param sampling Integer: Sampling frequency. If 100, means only every 100th simulation result will be written out. The first (start) and last (end) result will always be written out. Default = 100.
    @param resultfile String: Relative or absolute file path to write out sensitivity results. Default = 'sensitivity_analysis.csv'
    '''
    MSF = sensitivityGenerator(modelfile, multiple, prefix, mtype)
    outfmt = str(outfmt).lower()
    sampling = int(sampling)
    resultfile = os.path.abspath(resultfile)
    resultfile = open(resultfile, 'w')
    header = False
    msf_count = len(MSF)
    model_count = 0
    for param in MSF:
        model_count = model_count + 1
        # Generate ODE codes from model
        (spec, modelobj) = modelReader(MSF[param]['ASM'], 
                                    mtype, 'extended')
        print('Processing model %s of %s: %s' % \
            (model_count, msf_count, MSF[param]['ASM']))
        ODECode = ASModeller.generate_ODE(spec, modelobj, solver, 
                 timestep, endtime)
        odefile = re.sub('\.', '_', param)
        filepath = fileWriter(ODECode, 'models/temp', odefile + '.py')
        MSF[param]['ODE'] = filepath
        # Simulate ODE codes
        m = importlib.import_module('models.temp.'+ odefile)
        if header == False:
            labels = ['Parameter', 'Change'] + m.labels
            resultfile.write(','.join(labels) + '\n')
            header = True
        simData = []
        data_row_count = 0
        for data in m.model:
            if outfmt == "reduced":
                simData = [str(x) for x in data]
            elif outfmt == "full":
                if (data_row_count % sampling) == 0:
                    simData.append([str(x) for x in data])
                data_row_count = data_row_count + 1
        MSF[param]['Data'] = simData
        # Write out sensitivity results to resultfile
        if outfmt == "reduced":
            data = [param, MSF[param]['Change']] + MSF[param]['Data']
            data = [str(x) for x in data]
            resultfile.write(','.join(data) + '\n')
        elif outfmt == "full":
            for datarow in MSF[param]['Data']:
                data = [param, MSF[param]['Change']] + datarow
                data = [str(x) for x in data]
                resultfile.write(','.join(data) + '\n')
    resultfile.close()
    if str(cleanup).upper() == 'TRUE':
        for param in MSF:
            ASMfile = MSF[param]['ASM']
            ODEfile = MSF[param]['ODE']
            os.remove(ASMfile)
            os.remove(ODEfile)

def systemData():
    print('Welcome to AdvanceSyn Toolkit')
    print('')
    print('Current directory: %s' % os.getcwd())
    print('')

def installDependencies():
    '''!
    Function to install external tools and dependencies. List of external tools and dependencies that will be installed:

        - bokeh (https://bokeh.pydata.org), BSD 3-Clause "New" or 
        "Revised" License
        - cameo (https://github.com/biosustain/cameo), Apache 
        Licence 2.0

    Usage:

        python astools.py installdep
    '''
    # bokeh 
    try: 
        print('Check for presence of bokeh (https://bokeh.pydata.org)')
        import bokeh
        print('... bokeh found and importable')
    except ImportError:
        print('... bokeh not found ==> proceed to install bokeh')
        subprocess.check_call([sys.executable, '-m', 'pip', 
                               'install', 'bokeh', 
                               '--trusted-host', 'pypi.org', 
                               '--trusted-host', 'files.pythonhosted.org'])
        import bokeh
        print('... bokeh installed and importable')
    # cameo 
    try: 
        print('Check for presence of cameo (https://github.com/biosustain/cameo)')
        import cameo
        print('... cameo found and importable')
    except ImportError:
        print('... cameo not found ==> proceed to install cameo')
        subprocess.check_call([sys.executable, '-m', 'pip', 
                               'install', 'cameo', 
                               '--trusted-host', 'pypi.org', 
                               '--trusted-host', 'files.pythonhosted.org'])
        import cameo
        print('... cameo installed and importable')

def cameo_findPathway(model, product, max_prediction=4):
    import cameo
    ASExternalTools.find_pathway(model, product, 
                                 max_prediction)

def cameo_FBA(model, result_type='objective', library=False):
    '''!
    Function to simulate a model using Flux Balance Analysis (FBA), with Cameo.
    
    Usage:

        python astools.py cameo-fba --model=iJO1366 --result_type=objective

    @param model String: Model acceptable by Cameo (see http://cameo.bio/02-import-models.html).
    @param result_type String: Type of result to give. Allowable types are objective (objective value from FBA) or flux (table of fluxes). Default value = objective.
    @param library Boolean: Flag to use this function as a library function. If True, the results of execution will be returned in addition to printing on scree. Default = False.
    '''
    import cameo
    if library:
        return ASExternalTools.flux_balance_analysis(model, 'FBA', 
                                                     result_type)
    else: 
        ASExternalTools.flux_balance_analysis(model, 'FBA', result_type)

def cameo_pFBA(model, result_type='objective', library=False):
    '''!
    Function to simulate a model using Parsimonious Flux Balance Analysis (pFBA), with Cameo.

    pFBA reference: Lewis, N.E., Hixson, K.K., Conrad, T.M., Lerman, J.A., Charusanti, P., Polpitiya, A.D., Adkins, J.N., Schramm, G., Purvine, S.O., Lopez‐Ferrer, D. and Weitz, K.K., 2010. Omic data from evolved E. coli are consistent with computed optimal growth from genome‐scale models. Molecular Systems Biology, 6(1):390. http://www.ncbi.nlm.nih.gov/pubmed/20664636
    
    Usage:

        python astools.py cameo-pfba --model=iJO1366 --result_type=objective

    @param model String: Model acceptable by Cameo (see http://cameo.bio/02-import-models.html).
    @param result_type String: Type of result to give. Allowable types are objective (objective value from FBA) or flux (table of fluxes). Default value = objective.
    @param library Boolean: Flag to use this function as a library function. If True, the results of execution will be returned in addition to printing on scree. Default = False.
    '''
    import cameo
    if library:
        return ASExternalTools.flux_balance_analysis(model, 'pFBA', 
                                                     result_type)
    else:
        ASExternalTools.flux_balance_analysis(model, 'pFBA', result_type)
    
def cameo_reactionNames(model, library=False):
    '''!
    Function to list the reaction names in a model, with Cameo.

    Usage:

        python astools.py cameo-rxn-names --model=iJO1366

    @param model String: Model acceptable by Cameo (see http://cameo.bio/02-import-models.html).
    @param library Boolean: Flag to use this function as a library function. If True, the results of execution will be returned in addition to printing on scree. Default = False.
    '''
    import cameo
    if library:
        return ASExternalTools.get_reaction_names(model)
    else:
        ASExternalTools.get_reaction_names(model)

def cameo_reactionCompounds(model, library=False):
    '''!
    Function to list the reactants and products for each reaction in a model, with Cameo.

    Usage:

        python astools.py cameo-rxn-cpds --model=iJO1366

    @param model String: Model acceptable by Cameo (see http://cameo.bio/02-import-models.html).
    @param library Boolean: Flag to use this function as a library function. If True, the results of execution will be returned in addition to printing on scree. Default = False.
    '''
    import cameo
    if library:
        return ASExternalTools.get_reaction_compounds(model)
    else:
        ASExternalTools.get_reaction_compounds(model)

def cameo_mutantFBA(model, mutation, result_type='objective',
                    library=False):
    '''!
    Function to simulate a model after adding mutation(s) using Flux Balance Analysis (FBA), with Cameo.

    Usage:

        python astools.py cameo-mutant-fba --model=iJO1366 --mutation=NNAM,100,0;RBFK,0,0 --result_type=objective

    @param model String: Model acceptable by Cameo (see http://cameo.bio/02-import-models.html).
    @param mutation String: String to define mutation(s). Each mutation is defined as <reaction ID>:<upper bound>:<lower bound>. For example, RBFK,0,0 will represent a knock out. Multiple mutations are delimited using semicolon.
    @param result_type String: Type of result to give. Allowable types are objective (objective value from FBA) or flux (table of fluxes). Default value = objective.
    @param library Boolean: Flag to use this function as a library function. If True, the results of execution will be returned in addition to printing on scree. Default = False.
    '''
    import cameo
    if library:
        return ASExternalTools.mutantFBA(model, mutation, 'FBA', 
                                         result_type)
    else:
        ASExternalTools.mutantFBA(model, mutation, 'FBA', result_type)

def cameo_mutantpFBA(model, mutation, result_type='objective',
                     library=False):
    '''!
    Function to simulate a model after adding mutation(s) using Parsimonious Flux Balance Analysis (pFBA), with Cameo.

    pFBA reference: Lewis, N.E., Hixson, K.K., Conrad, T.M., Lerman, J.A., Charusanti, P., Polpitiya, A.D., Adkins, J.N., Schramm, G., Purvine, S.O., Lopez‐Ferrer, D. and Weitz, K.K., 2010. Omic data from evolved E. coli are consistent with computed optimal growth from genome‐scale models. Molecular Systems Biology, 6(1):390. http://www.ncbi.nlm.nih.gov/pubmed/20664636

    Usage:

        python astools.py cameo-mutant-pfba --model=iJO1366 --mutation=NNAM,100,0;RBFK,0,0 --result_type=objective

    @param model String: Model acceptable by Cameo (see http://cameo.bio/02-import-models.html).
    @param mutation String: String to define mutation(s). Each mutation is defined as <reaction ID>:<upper bound>:<lower bound>. For example, RBFK,0,0 will represent a knock out. Multiple mutations are delimited using semicolon.
    @param result_type String: Type of result to give. Allowable types are objective (objective value from FBA) or flux (table of fluxes). Default value = objective.
    @param library Boolean: Flag to use this function as a library function. If True, the results of execution will be returned in addition to printing on scree. Default = False.
    '''
    import cameo
    if library:
        return ASExternalTools.mutantFBA(model, mutation, 'pFBA', 
                                         result_type)
    else:
        ASExternalTools.mutantFBA(model, mutation, 'pFBA', result_type)

def cameo_medium(model, library=False):
    '''!
    Function to list the medium in a model, with Cameo.

    Usage:

        python astools.py cameo-medium-cpds --model=iAF1260

    @param model String: Model acceptable by Cameo (see http://cameo.bio/02-import-models.html).
    @param library Boolean: Flag to use this function as a library function. If True, the results of execution will be returned in addition to printing on scree. Default = False.
    '''
    import cameo
    if library:
        return ASExternalTools.get_medium(model)
    else:
        ASExternalTools.get_medium(model)

def cameo_mediumFBA(model, change, result_type='objective', 
                    library=False):
    '''!
    Function to simulate a model after adding media change(s) using Flux Balance Analysis (FBA), with Cameo.

    Usage:

        python astools.py cameo-medium-fba --model=iAF1260 --change=EX_o2_e,0;EX_glc__D_e,5.0 --result_type=objective

    @param model String: Model acceptable by Cameo (see http://cameo.bio/02-import-models.html).
    @param change String: String to define medium change(s). Each change is defined as <compound ID>:<new value>. For example, EX_o2_e,0 will represent anaerobic condition. Multiple changes are delimited using semicolon.
    @param result_type String: Type of result to give. Allowable types are objective (objective value from FBA) or flux (table of fluxes). Default value = objective.
    @param library Boolean: Flag to use this function as a library function. If True, the results of execution will be returned in addition to printing on scree. Default = False.
    '''
    import cameo
    if library:
        return ASExternalTools.mediumFBA(model, change, 'FBA', result_type)
    else:
        ASExternalTools.mediumFBA(model, change, 'FBA', result_type)

def cameo_mediumpFBA(model, change, result_type='objective', 
                     library=False):
    '''!
    Function to simulate a model after adding media change(s) using Parsimonious Flux Balance Analysis (pFBA), with Cameo.

    pFBA reference: Lewis, N.E., Hixson, K.K., Conrad, T.M., Lerman, J.A., Charusanti, P., Polpitiya, A.D., Adkins, J.N., Schramm, G., Purvine, S.O., Lopez‐Ferrer, D. and Weitz, K.K., 2010. Omic data from evolved E. coli are consistent with computed optimal growth from genome‐scale models. Molecular Systems Biology, 6(1):390. http://www.ncbi.nlm.nih.gov/pubmed/20664636

    Usage:

        python astools.py cameo-medium-pfba --model=iAF1260 --change=EX_o2_e,0;EX_glc__D_e,5.0 --result_type=objective

    @param model String: Model acceptable by Cameo (see http://cameo.bio/02-import-models.html).
    @param change String: String to define medium change(s). Each change is defined as <compound ID>:<new value>. For example, EX_o2_e,0 will represent anaerobic condition. Multiple changes are delimited using semicolon.
    @param result_type String: Type of result to give. Allowable types are objective (objective value from FBA) or flux (table of fluxes). Default value = objective.
    @param library Boolean: Flag to use this function as a library function. If True, the results of execution will be returned in addition to printing on scree. Default = False.
    '''
    import cameo
    if library:
        return ASExternalTools.mediumFBA(model, change, 'pFBA', result_type)
    else:
        ASExternalTools.mediumFBA(model, change, 'pFBA', result_type)

def GSM_to_ASM(model, name, outputfile, metabolite_initial=1e-5, 
               enzyme_conc=1e-6, enzyme_kcat=13.7, enzyme_km=130e-6):
    '''!
    Function to read reactions in Genome-Scale Models (GSM) using Cameo and convert to AdvanceSyn Model (ASM) format.

    Usage:

        python astools.py GSM-to-ASM --metabolite_initial=1e-5 --enzyme_conc=1e-6 --enzyme_kcat=13.7 --enzyme_km=130e-6 --model=e_coli_core --name=e_coli_core --outputfile=models/asm/e_coli_core.modelspec 

    @param model String: Model acceptable by Cameo (see http://cameo.bio/02-import-models.html).
    @param name String: Name of model author / creator.
    @param outputfile String: Relative path to the write out the converted ASM model.
    @param metabolite_initial Float: Initial metabolite concentration. Default = 1e-5 (10 uM).
    @param enzyme_conc Float: Enzyme concentration. Default = 1e-6 (1 uM)
    @param enzyme_kcat Float: Enzyme kcat / turnover number. Default = 13.7 (13.7 per second) based on Bar-Even et al (2011, 2015).
    @param enzyme_km Float: Enzyme Km (Michaelis-Menten constant). Default = 130e-6 (130 uM) based on Bar-Even et al (2011, 2015).
    '''
    rxnList = ASExternalTools.get_reaction_compounds(model, False)
    mediumConc = {}
    for mediacpd in ASExternalTools.get_medium(model, False):
        key = "m_" + mediacpd[1] + "_conc"
        mediumConc[key] = mediacpd[2]
    ASModeller.gsm_km_converter(model, name, outputfile, rxnList, 
                                metabolite_initial, enzyme_conc, 
                                enzyme_kcat, enzyme_km, mediumConc)
    return rxnList


exposed_functions = {
    # AdvanceSyn Toolkit Functions
    'genMO': generateModelObject,
    'genNetwork': generateNetwork,
    'genODE': generateODEScript,
    'GSM-to-ASM': GSM_to_ASM,
    'installdep': installDependencies,
    'LSA': localSensitivity,
    'mergeASM': mergeASM,
    'printASM': printASM,
    'readmodel': readModel,
    'readflux': readFluxes,
    'runODE': runODEScript,
    'senGen': sensitivityGenerator,
    'systemdata': systemData,
    # Cameo Functions
    'cameo-fba': cameo_FBA,
    'cameo-find-pathway': cameo_findPathway,
    'cameo-medium-cpds': cameo_medium,
    'cameo-medium-fba': cameo_mediumFBA,
    'cameo-medium-pfba': cameo_mediumpFBA,
    'cameo-mutant-fba': cameo_mutantFBA,
    'cameo-mutant-pfba': cameo_mutantpFBA,
    'cameo-pfba': cameo_pFBA,
    'cameo-rxn-cpds': cameo_reactionCompounds,
    'cameo-rxn-names': cameo_reactionNames
    }

function_descriptions = {
    'genMO': "Read the AdvanceSyn model specification file(s) and generate a file consisting of the internal model objects. Example: python astools.py genMO --prefix=exp --modelfile=models/asm/glycolysis.modelspec;models/asm/RFPproduction.modelspec --outputfile=models/mo/glycolysis.mo",
    'genNetwork': "Read the AdvanceSyn model specification file(s) and generate a network / reaction visualization file. Example: python astools.py genNetwork --outfmt=SIF --modelfile=models/asm/glycolysis.modelspec;models/asm/ppp.modelspec --outputfile=glycolysis_ppp.sif",
    'genODE': "Generate Python ODE script from a given model specification file. Example: python astools.py genODE --modelfile=models/asm/glycolysis.modelspec --mtype=ASM --solver=RK4 --timestep=1 --endtime=21600 --lowerbound=0;0 --upperbound=1e-3;1e-3 --odefile=glycolysis.py",
    'GSM-to-ASM': "Read reactions in Genome-Scale Models (GSM) using Cameo and convert to AdvanceSyn Model (ASM) format. Example: python astools.py GSM-to-ASM --metabolite_initial=1e-5 --enzyme_conc=1e-6 --enzyme_kcat=13.7 --enzyme_km=130e-6 --model=e_coli_core --name=e_coli_core --outputfile=models/asm/e_coli_core.modelspec",
    'installdep': "Install external tools and dependencies. Example: python astools.py installdep",
    'LSA': "Perform local sensitivity analysis using OFAT/OAT (one factor at a time) method where the last data time (end time) simulation results are recorded into results file. Example: python astools.py LSA --modelfile=models/asm/glycolysis.modelspec --prefix=sen01 --mtype=ASM --multiple=100 --solver=RK4 --timestep=1 --endtime=21600 --cleanup=True --outfmt=reduced --resultfile=sensitivity_analysis.csv",
    'mergeASM': "Read the AdvanceSyn model specification file(s) and merge them into a single AdvanceSyn model specification file. Example: python astools.py mergeASM --prefix=exp --modelfile=models/asm/glycolysis.modelspec;models/asm/ppp.modelspec --outputfile=models/asm/glycolysis_ppp.modelspec",
    'printASM': "Read the AdvanceSyn model specification file and print out its details before processing into model objects. Example: python astools.py printASM --modelfile=models/asm/glycolysis.modelspec --readertype=extended",
    'readmodel': "Read a model file and print out its details after processing into model objects. Example: python astools.py readmodel --mtype=ASM --modelfile=models/asm/glycolysis.modelspec",
    'readflux': "Read the AdvanceSyn model objects file and print out fluxes (productions and usages) of model objects. Example: python astools.py readflux --mtype=ASM --modelfile=models/asm/glycolysis.modelspec",
    'runODE': "Run / execute the ODE model and write out the simulation results. Example: python astools.py runODE --odefile=glycolysis.py --sampling=500 --resultfile=oderesult.csv",
    'senGen': "Generate a series of AdvanceSyn Model Specifications from an existing model by multiplying a multiple to the variable in preparation for sensitivity analyses. Example: python astools.py senGen --modelfile=models/asm/glycolysis.modelspec --prefix=sen01 --mtype=ASM --multiple=100",
    'systemdata': "Prints out system information. Example: pathon astools.py systemdata",
    'cameo-fba': "Simulate a model using Flux Balance Analysis (FBA), with Cameo. Example: python astools.py cameo-fba --model=iJO1366 --result_type=objective",
    'cameo-find-pathway': "cameo_findPathway",
    'cameo-medium-cpds': "List the medium in a model, with Cameo. Example: python astools.py cameo-medium-cpds --model=iAF1260",
    'cameo-medium-fba': "Simulate a model after adding media change(s) using Flux Balance Analysis (FBA), with Cameo. Example: python astools.py cameo-medium-fba --model=iAF1260 --change=EX_o2_e,0;EX_glc__D_e,5.0 --result_type=objective",
    'cameo-medium-pfba': "simulate a model after adding media change(s) using Parsimonious Flux Balance Analysis (pFBA), with Cameo. Example: python astools.py cameo-medium-pfba --model=iAF1260 --change=EX_o2_e,0;EX_glc__D_e,5.0 --result_type=objective",
    'cameo-mutant-fba': "Simulate a model after adding mutation(s) using Flux Balance Analysis (FBA), with Cameo. Example: python astools.py cameo-mutant-fba --model=iJO1366 --mutation=NNAM,100,0;RBFK,0,0 --result_type=objective",
    'cameo-mutant-pfba': "Simulate a model after adding mutation(s) using Parsimonious Flux Balance Analysis (pFBA), with Cameo. Example: python astools.py cameo-mutant-pfba --model=iJO1366 --mutation=NNAM,100,0;RBFK,0,0 --result_type=objective",
    'cameo-pfba': "Simulate a model using Parsimonious Flux Balance Analysis (pFBA), with Cameo. Example: python astools.py cameo-pfba --model=iJO1366 --result_type=objective",
    'cameo-rxn-cpds': "List the reactants and products for each reaction in a model, with Cameo. Example: python astools.py cameo-rxn-cpds --model=iJO1366",
    'cameo-rxn-names': "List the reaction names in a model, with Cameo. Example: python astools.py cameo-rxn-names --model=iJO1366"
}

def extract_param_help(docstring):
    """
    Extract @param descriptions from docstring.

    Returns:
        Dict[str, str]
    """
    param_help = {}
    if not docstring:
        return param_help

    for line in docstring.splitlines():
        line = line.strip()
        match = re.match(r"@param\s+(\w+)\s+[\w\[\]]+:\s+(.*)", line)
        if match:
            param, desc = match.groups()
            param_help[param] = desc
    return param_help

def main():
    parser = argparse.ArgumentParser(description="AdvanceSyn Toolkit")
    subparsers = parser.add_subparsers(dest='command', required=True)

    for name, func in exposed_functions.items():
        # Inspect function signature
        doc = func.__doc__ or ""
        param_help_map = extract_param_help(doc)

        subparser = subparsers.add_parser(name, help=function_descriptions[name], description=function_descriptions[name])
        try:
            sig = inspect.signature(func)
            for param in sig.parameters.values():
                arg_name = f"--{param.name}"
                is_required = param.default is param.empty
                help_text = param_help_map.get(param.name, f"{param.name} parameter")
                subparser.add_argument(
                    arg_name,
                    required=is_required,
                    help=help_text
                )
        except Exception as e:
            print(f"Error inspecting function {name}: {e}")
            subparser.add_argument('--args', nargs=argparse.REMAINDER)

    args = parser.parse_args()
    func = exposed_functions[args.command]

    # Filter args to function params
    func_args = vars(args).copy()
    del func_args['command']
    result = func(**func_args)
    if result is not None:
        print(result)


if __name__ == '__main__':
    main()

