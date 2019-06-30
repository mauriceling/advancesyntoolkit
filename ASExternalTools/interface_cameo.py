'''
AdvanceSyn Toolkit / Cameo Interface.

Date created: 22nd March 2019

This file contains functions to interface between AdvanceSyn 
Toolkit and Cameo (https://github.com/biosustain/cameo).

Cameo reference: Cardoso, J.G., Jensen, K., Lieven, C., Lærke 
Hansen, A.S., Galkina, S., Beber, M., Ozdemir, E., Herrgård, M.J., 
Redestig, H. and Sonnenschein, N., 2018. Cameo: a Python library 
for computer aided metabolic engineering and optimization of cell 
factories. ACS synthetic biology, 7(4), pp.1163-1166.

Copyright (c) 2019, AdvanceSyn Private Limited.

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

def _cameo_header():
    text = '''
This operation uses Cameo (https://github.com/biosustain/cameo). If you used it in your study, please cite: Cardoso, J.G., Jensen, K., Lieven, C., Lærke Hansen, A.S., Galkina, S., Beber, M., Ozdemir, E., Herrgård, M.J., Redestig, H. and Sonnenschein, N., 2018. Cameo: a Python library for computer aided metabolic engineering and optimization of cell factories. ACS synthetic biology, 7(4), pp.1163-1166.
    '''
    print(text)
    print('')

def get_reaction_names(model, pflag=True):
    '''!
    Function to list the reaction names in a model, with Cameo.

    @model String: Model acceptable by Cameo (see 
    http://cameo.bio/02-import-models.html).
    @pflag Boolean: Flag to enable printing of results. Default = 
    True (results are printed).
    '''
    import cameo
    _cameo_header()
    print('Load model: %s' % str(model))
    model = cameo.load_model(model)
    print('')
    count = 1
    result = []
    if pflag:
        print('Number : Reaction ID : Upper Bound : Lower Bound : Reaction Name')
    for rxn in model.reactions:
        if pflag:
            print('%s : %s : %s : %s : %s' % \
                  (count, rxn.id, rxn.upper_bound, 
                   rxn.lower_bound, rxn.name))
        result.append([count, rxn.id, rxn.upper_bound, 
                       rxn.lower_bound, rxn.name])
        count = count + 1
    return result

def get_reaction_compounds(model, pflag=True):
    '''!
    Function to list the reactants and products for each reaction 
    in a model, with Cameo.

    @model String: Model acceptable by Cameo (see 
    http://cameo.bio/02-import-models.html).
    @pflag Boolean: Flag to enable printing of results. Default = 
    True (results are printed).
    '''
    import cameo
    _cameo_header()
    print('Load model: %s' % str(model))
    model = cameo.load_model(model)
    print('')
    count = 1
    result = []
    if pflag:
        print('Number : Reaction ID : Reactants : Products : Reaction Name')
    for rxn in model.reactions:
        rxn_id = rxn.id
        rxn_name = rxn.name
        reactants = [r.id for r in rxn.reactants]
        products = [p.id for p in rxn.products]
        if pflag:
            print('%s : %s : %s : %s : %s' % \
                  (count, rxn_id, '|'.join(reactants), 
                   '|'.join(products), rxn.name))
        result.append([count, rxn_id, reactants, 
                       products, rxn.name])
        count = count + 1
    return result

def get_medium(model, pflag=True):
    '''!
    Function to list the medium in a model, with Cameo.

    @model String: Model acceptable by Cameo (see 
    http://cameo.bio/02-import-models.html).
    @pflag Boolean: Flag to enable printing of results. Default = 
    True (results are printed).
    '''
    import cameo
    _cameo_header()
    print('Load model: %s' % str(model))
    model = cameo.load_model(model)
    medium = model.medium
    print('')
    count = 1
    result = []
    if pflag:
        print('Number : Component : Rate (mmol/gDW/h)')
    for cpd in medium:
        if pflag:
            print('%s : %s : %s' % \
                  (count, cpd, str(medium[cpd])))
        result.append([count, cpd, str(medium[cpd])])
        count = count + 1
    return result

def find_pathway(model, product, max_prediction=4):
    import cameo
    _cameo_header()
    model = cameo.load_model(model)
    predictor = cameo.strain_design.pathway_prediction.PathwayPredictor(model)
    pathways = predictor.run(product=str(product), 
                             max_predictions=max_predictions)
    for rxnID in pathways.pathways[0].data_frame['equation'].keys():
        print()

def _fba(model, analysis):
    '''!
    Private function - to simulate a model using Flux Balance 
    Analysis (FBA) or FBA-related methods, with Cameo.

    @model String: Model acceptable by Cameo (see 
    http://cameo.bio/02-import-models.html).
    @analysis String: Type of FBA to perform. Allowable types are 
    FBA (standard flux balance analysis) and pFBA (parsimonious 
    FBA). 
    '''
    import cameo
    if analysis == 'FBA':
        print('Run flux balance analysis on model %s' % str(model))
        return cameo.fba(model)
    elif analysis =='pFBA':
        print('Run parsimonious flux balance analysis on model %s' \
              % str(model))
        return cameo.pfba(model)

def _fba_result(result, result_type, analysis, pflag=True):
    '''!
    Private function - to print out results from FBA analysis.

    @result Object: Result object from FBA.
    @result_type String: Type of result to give. Allowable types 
    are objective (objective value from FBA) or flux (table of 
    fluxes).
    @analysis String: Type of FBA to perform. Allowable types are 
    FBA (standard flux balance analysis) and pFBA (parsimonious 
    FBA).
    @pflag Boolean: Flag to enable printing of results. Default = 
    True (results are printed).
    @return: Required results from FBA result object.
    '''
    if result_type == 'objective' and analysis == 'FBA':
        result = abs(result.data_frame.flux).sum()
        if pflag: 
            print('Objective value = %s' % result)
        return result
    if result_type == 'objective' and analysis == 'pFBA':
        if pflag:
            print('Objective value = %s' % result.objective_value)
        return result.objective_value
    elif result_type == 'flux':
        return_result = []
        for metabolite in result.data_frame['flux'].keys():
            if pflag:
                print('%s : %s' % \
                    (metabolite, 
                     result.data_frame['flux'][metabolite]))
            return_result.append([metabolite, 
                           result.data_frame['flux'][metabolite]])
        return return_result

def flux_balance_analysis(model, analysis='FBA',
                          result_type='objective',
                          pflag=True):
    '''!
    Function to simulate a model using Flux Balance Analysis (FBA) 
    or FBA-related methods, with Cameo.

    @model String: Model acceptable by Cameo (see 
    http://cameo.bio/02-import-models.html).
    @analysis String: Type of FBA to perform. Allowable types are 
    FBA (standard flux balance analysis) and pFBA (parsimonious 
    FBA). Default value = FBA.
    @pflag Boolean: Flag to enable printing of results. Default = 
    True (results are printed).
    @result_type String: Type of result to give. Allowable types 
    are objective (objective value from FBA) or flux (table of 
    fluxes).
    '''
    import cameo
    _cameo_header()
    print('Load model: %s' % str(model))
    model = cameo.load_model(model)
    result = _fba(model, analysis)
    result = _fba_result(result, result_type, analysis, pflag)
    return result

def _parse_mutation(mutation):
    '''!
    Private function - to process mutation definition into 
    dictionary format. For example, RBFK,0,0 to {'RBFK': (0,0)}.

    @mutation String: String to define mutation(s). Each mutation 
    is defined as <reaction ID>:<upper bound>:<lower bound>. For 
    example, RBFK,0,0 will represent a knock out. Multiple mutations 
    are delimited using semicolon.
    @return: Dictionary to represent mutation(s)
    '''
    mutation = str(mutation)
    mutation = [pair.strip() for pair in mutation.split(';')]
    mutation = [[pair.split(',')[0], 
                 pair.split(',')[1], 
                 pair.split(',')[2]] 
                 for pair in mutation]
    mutation = [[pair[0].strip(), 
                 pair[1].strip(), 
                 pair[2].strip()] 
                 for pair in mutation]
    ndict = {}
    for k in mutation:
        ndict[str(k[0])] = (int(k[1]), int(k[2]))
    return ndict

def _perform_mutation(model, mutation):
    '''!
    Private method - to change the upper and lower bounds of one 
    or more reactions to represent one or more mutations.

    @model Object: Cameo model object
    @return: model with flux change(s) (representing mutation(s))
    '''
    print('Process mutation(s) ... ')
    for metabolite in mutation:
        for i in range(len(model.reactions)):
            if model.reactions[i].id == metabolite:
                print('Metabolite %s found' % metabolite)
                ori_ub = model.reactions[i].upper_bound
                ori_lb = model.reactions[i].lower_bound
                model.reactions[i].upper_bound = \
                    mutation[metabolite][0]
                model.reactions[i].lower_bound = \
                    mutation[metabolite][1]
                new_ub = model.reactions[i].upper_bound
                new_lb = model.reactions[i].lower_bound
                print('... Upper Bound: %s --> %s' % \
                    (ori_ub, new_ub))
                print('... Lower Bound: %s --> %s' % \
                    (ori_lb, new_lb))
    return model

def mutantFBA(model, mutation, analysis='FBA',
              result_type='objective', pflag=True):
    '''!
    Function to simulate a model after adding mutation(s) using 
    Flux Balance Analysis (FBA) or FBA-related methods, with Cameo.

    @model String: Model acceptable by Cameo (see 
    http://cameo.bio/02-import-models.html).
    @mutation String: String to define mutation(s). Each mutation 
    is defined as <reaction ID>:<upper bound>:<lower bound>. For 
    example, RBFK,0,0 will represent a knock out. Multiple mutations 
    are delimited using semicolon.
    @analysis String: Type of FBA to perform. Allowable types are 
    FBA (standard flux balance analysis) and pFBA (parsimonious 
    FBA). Default value = FBA.
    @pflag Boolean: Flag to enable printing of results. Default = 
    True (results are printed).
    @result_type String: Type of result to give. Allowable types 
    are objective (objective value from FBA) or flux (table of 
    fluxes).
    '''
    import cameo
    _cameo_header()
    print('Load model: %s' % str(model))
    model = cameo.load_model(model)
    mutation = _parse_mutation(mutation)
    model = _perform_mutation(model, mutation)
    result = _fba(model, analysis)
    result = _fba_result(result, result_type, analysis, pflag)
    return result

def _parse_medium_change(change):
    '''!
    Private function - to process medium change definition into 
    dictionary format. For example, EX_o2_e,0 to {'EX_o2_e': 0}.

    @change String: String to define medium change(s). Each change
    is defined as <compound ID>:<new value>. For example, EX_o2_e,0 
    will represent anaerobic condition. Multiple changes are delimited 
    using semicolon.
    @return: Dictionary to represent change(s)
    '''
    change = str(change)
    change = [pair.strip() for pair in change.split(';')]
    change = [[pair.split(',')[0], 
               pair.split(',')[1]] 
              for pair in change]
    change = [[pair[0].strip(), 
              pair[1].strip()] 
             for pair in change]
    ndict = {}
    for k in change:
        key = str(k[0])
        value = str(k[1])
        # Extra start characters
        if key.startswith("('"): key = key[2:]
        elif key.startswith("("): key = key[1:]
        elif key.startswith("'"): key = key[1:]
        if value.startswith("('"): value = value[2:]
        elif value.startswith("("): value = value[1:]
        elif value.startswith("'"): value = value[1:]
        # Extra end characters
        if key.endswith("')"): key = key[:-2]
        elif key.endswith(")"): key = key[:-1]
        elif key.endswith("'"): key = key[:-1]
        if value.endswith("')"): value = value[:-2]
        elif value.endswith(")"): value = value[:-1]
        elif value.endswith("'"): value = value[:-1]
        # Assigning to dictionary
        ndict[key] = float(value)
    return ndict

def _perform_medium_change(model, change):
    '''!
    Private method - to change the upper and lower bounds of one 
    or more reactions to represent one or more mutations.

    @model Object: Cameo model object
    @return: model with flux change(s) (representing mutation(s))
    '''
    print('Process medium change(s) ... ')
    medium = model.medium
    for compound in change:
        if compound in medium:
            print('Compound %s found' % compound)
            original_conc = medium[compound]
            medium[compound] = change[compound]
            print('... Change: %s --> %s' % \
                (str(original_conc), str(change[compound])))
    model.medium = medium
    return model

def mediumFBA(model, change, analysis='FBA',
              result_type='objective', pflag=True):
    '''!
    Function to simulate a model after changing medium conditions(s) 
    using Flux Balance Analysis (FBA) or FBA-related methods, with 
    Cameo.

    @model String: Model acceptable by Cameo (see 
    http://cameo.bio/02-import-models.html).
    @change String: String to define medium change(s). Each change
    is defined as <compound ID>:<new value>. For example, EX_o2_e,0 
    will represent anaerobic condition. Multiple changes are delimited 
    using semicolon.
    @analysis String: Type of FBA to perform. Allowable types are 
    FBA (standard flux balance analysis) and pFBA (parsimonious 
    FBA). Default value = FBA.
    @pflag Boolean: Flag to enable printing of results. Default = 
    True (results are printed).
    @result_type String: Type of result to give. Allowable types 
    are objective (objective value from FBA) or flux (table of 
    fluxes).
    '''
    import cameo
    _cameo_header()
    print('Load model: %s' % str(model))
    model = cameo.load_model(model)
    change = _parse_medium_change(change)
    model = _perform_medium_change(model, change)
    result = _fba(model, analysis)
    result = _fba_result(result, result_type, analysis, pflag)
    return result