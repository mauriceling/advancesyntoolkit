'''
Functions to merge several sets of model objects into a single 
set of model objects.

Date created: 17th February 2019

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

def _renumberReactions(modelnumber, count, 
                       spec, modelobj, prefix='exp',
                       p_spec=True, p_modelobj=True):
    '''!
    Private function - used by renameReactions() to renumber all 
    reactions in a single model specification and the corresponding 
    list of model objects.

    @param modelnumber Integer: Numerical order of models for 
    processing - this is used for print statements.
    @param count Integer: Numerical numbering for the next reaction 
    count to use.
    @param spec Object: Model specfication object as ConfigParser 
    object.
    @param modelobj Object: Model specfication object as ConfigParser 
    object.
    @param prefix String: Prefix for new reaction IDs. This prefix 
    cannot be any existing prefixes in any of the model specifications 
    to be merged. Default = 'exp'.
    @param p_spec Boolean: Flag to determine whether reactions 
    in model specification (spec) should be renumbered. Default = 
    True (reactions in spec to be renumbered).
    @param p_modelobj Boolean: Flag to determine whether 
    reactions in model objects (modelobj) should be renumbered. 
    Default = True (reactions in modelobj to be renumbered).
    @return: (reaction renumbered specification, list of reaction 
    renumbered model objects, next reaction count)
    '''
    if p_spec:
        print('Renaming / Renumbering Reactions in Specification ' + \
            str(modelnumber))
        table = {}
        # Step 1: Generate reaction renumbering table
        for rxn_ID in spec['Reactions']:
            table[rxn_ID] = str(prefix) + str(count)
            count = count + 1
        # Step 2: Renumber specification
        for rxn_ID in spec['Reactions']:
            newID = table[rxn_ID]
            spec['Reactions'][newID] = spec['Reactions'][rxn_ID]
            del spec['Reactions'][rxn_ID]
            print('  Specification %s: %s --> %s' % \
                (modelnumber, rxn_ID, newID))
        print('')
    if p_modelobj:
    # Step 3: Renumbering model objects
        print('  Number of Model Objects in Specification %s: %s' \
            % (modelnumber, len(modelobj)))
        print('')
        index = 1
        for name in modelobj:
            mobj = modelobj[name]
            print('  Object Name / Description %s: %s | %s' % \
                (index, mobj.name, mobj.description))
            print('')
            index = index + 1
            for key in list(mobj.influx.keys()):
                newID = table[key]
                mobj.influx[newID] = mobj.influx[key]
                del mobj.influx[key]
                print('    Influx %s --> %s' % (key, newID))
            for key in list(mobj.outflux.keys()):
                newID = table[key]
                mobj.outflux[newID] = mobj.outflux[key]
                del mobj.outflux[key]
                print('    Outflux %s --> %s' % (key, newID))
            print('')
    '''
    for key in spec['Reactions']:
        print('%s / %s' % (key, spec['Reactions'][key]))
    '''
    return (spec, modelobj, count)

def renameReactions(specList, modelobjList, prefix='exp',
                    p_specList=True, p_modelobjList=True):
    '''!
    Function to renumber all reactions in model specifications and 
    model objects. This is necessary to prevent duplicated reaction 
    IDs, which will cause errors during model merging as reaction 
    IDs are used as keys in various dictionaries; thus, it is 
    necessary to have unique reaction IDs across the multiple 
    model specifications to be merged.

    @param specList List: List of AdvanceSyn model specifications 
    as ConfigParser objects.
    @param modelobjList List: List of model objects where each 
    model objects is a list of model objects representing the 
    corresponding (by index) model specification in specList.
    @param prefix String: Prefix for new reaction IDs. This prefix 
    cannot be any existing prefixes in any of the model specifications 
    to be merged. Default = 'exp'.
    @param p_specList Boolean: Flag to determine whether reactions 
    in specList should be renumbered. Default = True (reactions 
    in specList to be renumbered).
    @param p_modelobjList Boolean: Flag to determine whether 
    reactions in modelobjList should be renumbered. Default = True 
    (reactions in modelobjList to be renumbered).
    @return: (reaction renumbered specification list, list of 
    reaction renumbered model object list)
    '''
    count = 1
    for index in range(len(specList)):
        (spec, 
         modelobj,
         count) = _renumberReactions(index+1, count,
                                     specList[index], 
                                     modelobjList[index],
                                     prefix,
                                     p_specList, 
                                     p_modelobjList)
        specList[index] = spec
        modelobjList[index] = modelobj
    return (specList, modelobjList)

def mergeSpecification(spec, specList):
    '''!
    Function to merge a list of model specifications into a given 
    model specification

    @param spec Object: Model specfication object as ConfigParser 
    object.
    @param specList List: List of model specification objects 
    where each element is a ConfigParser object.
    @return: Merged model specification object as ConfigParser 
    object.
    '''
    print('Merge Specifications ...')
    statistics = {'Identifiers': [len(spec['Identifiers'])],
                  'Objects': [len(spec['Objects'])],
                  'Initials': [len(spec['Initials'])],
                  'Variables': [len(spec['Variables'])],
                  'Reactions': [len(spec['Reactions'])]}
    for s in specList:
        # Step 1: Merge identifiers
        for key in s['Identifiers']:
            count = 1
            newkey = key + '_' + str(count)
            spec['Identifiers'][newkey] = s['Identifiers'][key]
            count = count + 1
        number = len(s['Identifiers'])
        statistics['Identifiers'].append(number)
        # Step 2: Merge objects
        for key in s['Objects']:
            spec['Objects'][key] = s['Objects'][key]
        number = len(s['Objects'])
        statistics['Objects'].append(number)
        # Step 3: Merge initials
        for key in s['Initials']:
            spec['Initials'][key] = s['Initials'][key]
        number = len(s['Initials'])
        statistics['Initials'].append(number)
        # Step 4: Merge variables
        for key in s['Variables']:
            spec['Variables'][key] = s['Variables'][key]
        number = len(s['Variables'])
        statistics['Variables'].append(number)
        # Step 5: Merge reactions
        for key in s['Reactions']:
            spec['Reactions'][key] = s['Reactions'][key]
        number = len(s['Reactions'])
        statistics['Reactions'].append(number)
    '''
    for stanza in spec:
        for key in spec[stanza]:
            print('%s / %s / %s' % \
                  (stanza, key, spec[stanza][key]))
    '''
    print('Numbers of Identifiers = %s' % \
        ', '.join([str(x) for x in statistics['Identifiers']]))
    print('... Total Numbers of Identifiers = %s' % \
        str(sum(statistics['Identifiers'])))
    print('Numbers of Objects = %s' % \
        ', '.join([str(x) for x in statistics['Objects']]))
    print('... Total Numbers of Objects = %s' % \
        str(sum(statistics['Objects'])))
    print('Numbers of Initials = %s' % \
        ', '.join([str(x) for x in statistics['Initials']]))
    print('... Total Numbers of Initials = %s' % \
        str(sum(statistics['Initials'])))
    print('Numbers of Variables = %s' % \
        ', '.join([str(x) for x in statistics['Variables']]))
    print('... Total Numbers of Variables = %s' % \
        str(sum(statistics['Variables'])))
    print('Numbers of Reactions = %s' % \
        ', '.join([str(x) for x in statistics['Reactions']]))
    print('... Total Numbers of Reactions = %s' % \
        str(sum(statistics['Reactions'])))
    print('')
    return spec

def mergeModelObjects(modelobj, modelobjList):
    '''!
    Function to merge a 2-dimensional list of model objects, where 
    the first dimension is a list of model objects representing 
    the a corresponding model specification, into a given list of 
    model objects.

    @param modelobj List: List of model objects for all model 
    objects in modelobjList to merge into.
    @param modelobjList List: List of list of model objects where 
    each first-level element is a list of model objects representing 
    the a corresponding model specification.
    @return: List of merged model objects.
    '''
    print('Merging Model Objects ...')
    objcount = [len(modelobj)] + [len(x) for x in modelobjList]
    print('Number of Model Objects: %s' % \
        ', '.join([str(x) for x in objcount]))
    print('... Total Numbers of Model Objects = %s' % \
        str(sum(objcount)))
    print('')
    objectNames = list(modelobj.keys())
    spec_count = 1
    print('  Names of Model Objects from Specification %s: %s' \
        % (spec_count, ' | '.join(objectNames)))
    print('')
    for mobjs in modelobjList:
        print('  Number of Merged Model Objects: %s' \
        % len(objectNames))
        print('  Current Names of Merged Model Objects: %s' \
        % ' | '.join(objectNames))
        print('')
        spec_count = spec_count + 1
        print('  Names of Model Objects from Specification %s: %s' \
            % (spec_count, ' | '.join(list(mobjs.keys()))))
        print('')
        for name in mobjs:
            if name not in objectNames:
                print('    %s object is not in current merged list - full model object merge' \
                    % name)
                modelobj[name] = mobjs[name]
                objectNames.append(name)
            else:
                print('    %s object is in current merged list - merge fluxes' \
                    % name)
                cobj = modelobj[name]
                c_in = [cobj.influx[k] for k in cobj.influx]
                c_out = [cobj.outflux[k] for k in cobj.outflux]
                nobj = mobjs[name]
                for k in nobj.influx:
                    if nobj.influx[k] not in c_in:
                        print('    Influx (%s) in %s is not present in current object - influx merged' \
                            % (nobj.influx[k], name))
                        cobj.influx[k] = nobj.influx[k]
                    else:
                        print('    Influx (%s) in %s is already present in current object - influx not merged' \
                            % (nobj.influx[k], name))
                for k in nobj.outflux:
                    if nobj.outflux[k] not in c_out:
                        print('    Outflux (%s) in %s is not present in current object - outflux merged' \
                            % (nobj.outflux[k], name))
                        cobj.outflux[k] = nobj.outflux[k]
                    else:
                        print('    Outflux (%s) in %s is already present in current object - outflux not merged' \
                            % (nobj.outflux[k], name))
        print('')
    print('  Number of Merged Model Objects: %s' % \
        len(objectNames))
    print('  Current Names of Merged Model Objects: %s' % \
        ' | '.join(objectNames))
    print('')
    return modelobj

def modelMerge(specList, modelobjList, prefix='exp',
               p_specList=True, p_modelobjList=True):
    '''!
    Function to merge a list of AdvanceSyn model specifications 
    and model objects into a single specification and object. This 
    function is the interface for models merging.

    @param specList List: List of AdvanceSyn model specifications 
    as ConfigParser objects.
    @param modelobjList List: List of model objects where each 
    model objects is a list of model objects representing the 
    corresponding (by index) model specification in specList.
    @param prefix String: Prefix for new reaction IDs. This prefix 
    cannot be any existing prefixes in any of the model specifications 
    to be merged. Default = 'exp'.
    @param p_specList Boolean: Flag to determine whether specList 
    should be merged. If not merged, the returned merged 
    specification will be None. Default = True (specList to be 
    merged).
    @param p_modelobjList Boolean: Flag to determine whether 
    modelobjList should be merged. If not merged, the returned list 
    of merged model objects will be None. Default = True 
    (modelobjList to be merged).
    @return: (merged specification, list of merged model objects)
    '''
    (specList, modelobjList) = renameReactions(specList, 
                                               modelobjList,
                                               prefix,
                                               p_specList, 
                                               p_modelobjList)
    if p_specList and \
        specList != None and len(specList) > 0:
        merged_spec = specList[0]
        specList = specList[1:]
        merged_spec = mergeSpecification(merged_spec, specList)
    else:
        merged_spec = None
    if p_modelobjList and \
        modelobjList != None and len(modelobjList) > 0:
        merged_modelobj = modelobjList[0]
        modelobjList = modelobjList[1:]
        merged_modelobj = mergeModelObjects(merged_modelobj, 
                                            modelobjList)
    else:
        merged_modelobj = None
    return (merged_spec, merged_modelobj)
