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

def get_reaction_names(model):
    '''!
    Function to list the reaction names in a model, with Cameo.

    @model String: Model acceptable by Cameo (see 
    http://cameo.bio/02-import-models.html).
    '''
    import cameo
    _cameo_header()
    print('Load model: %s' % str(model))
    model = cameo.load_model(model)
    print('')
    count = 1
    print('Number : Reaction ID : Upper Bound : Lower Bound : Reaction Name')
    for rxn in model.reactions:
        print('%s : %s : %s : %s : %s' % \
              (count, rxn.id, rxn.upper_bound, 
               rxn.lower_bound, rxn.name))
        count = count + 1

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

def _fba_result(result, result_type, analysis):
    '''!
    Private function - to print out results from FBA analysis.

    @result Object: Result object from FBA.
    @result_type String: Type of result to give. Allowable types 
    are objective (objective value from FBA) or flux (table of 
    fluxes).
    @analysis String: Type of FBA to perform. Allowable types are 
    FBA (standard flux balance analysis) and pFBA (parsimonious 
    FBA).
    '''
    if result_type == 'objective' and analysis == 'FBA':
        print('Objective value = %s' % \
            abs(result.data_frame.flux).sum())
    if result_type == 'objective' and analysis == 'pFBA':
        print('Objective value = %s' % result.objective_value)
    elif result_type == 'flux':
        for metabolite in result.data_frame['flux'].keys():
            print('%s : %s' % \
                (metabolite, 
                 result.data_frame['flux'][metabolite]))

def flux_balance_analysis(model, analysis='FBA',
                          result_type='objective'):
    '''!
    Function to simulate a model using Flux Balance Analysis (FBA) 
    or FBA-related methods, with Cameo.

    @model String: Model acceptable by Cameo (see 
    http://cameo.bio/02-import-models.html).
    @analysis String: Type of FBA to perform. Allowable types are 
    FBA (standard flux balance analysis) and pFBA (parsimonious 
    FBA). Default value = FBA.
    @result_type String: Type of result to give. Allowable types 
    are objective (objective value from FBA) or flux (table of 
    fluxes).
    '''
    import cameo
    _cameo_header()
    print('Load model: %s' % str(model))
    model = cameo.load_model(model)
    result = _fba(model, analysis)
    _fba_result(result, result_type, analysis)

def _parse_mutation(mutation):
    '''!
    Private function - to process mutation definition into 
    dictionary format. For example, RBFK,0,0 to {'RBFK': (0,0)}.

    @mutation String: String to define mutation(s). Each mutation 
    is defined as <rection ID>:<upper bound>:<lower bound>. For 
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

def mutantFBA(model, mutation, 
              analysis='FBA',
              result_type='objective'):
    '''!
    Function to simulate a model after adding mutation(s) using 
    Flux Balance Analysis (FBA) or FBA-related methods, with Cameo.

    @model String: Model acceptable by Cameo (see 
    http://cameo.bio/02-import-models.html).
    @mutation String: String to define mutation(s). Each mutation 
    is defined as <rection ID>:<upper bound>:<lower bound>. For 
    example, RBFK,0,0 will represent a knock out. Multiple mutations 
    are delimited using semicolon.
    @analysis String: Type of FBA to perform. Allowable types are 
    FBA (standard flux balance analysis) and pFBA (parsimonious 
    FBA). Default value = FBA.
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
    _fba_result(result, result_type, analysis)
