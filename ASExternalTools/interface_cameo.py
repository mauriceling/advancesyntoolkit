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
This operation uses Cameo (https://github.com/biosustain/cameo). If you used it in your study, please cite 

Cardoso, J.G., Jensen, K., Lieven, C., Lærke Hansen, A.S., Galkina, S., Beber, M., Ozdemir, E., Herrgård, M.J., Redestig, H. and Sonnenschein, N., 2018. Cameo: a Python library for computer aided metabolic engineering and optimization of cell factories. ACS synthetic biology, 7(4), pp.1163-1166.
    '''
    print(text)
    print('')

def find_pathway(model, product, max_prediction=4):
    import cameo
    _cameo_header()
    model = cameo.load_model(model)
    predictor = cameo.strain_design.pathway_prediction.PathwayPredictor(model)
    pathways = predictor.run(product=str(product), 
                             max_predictions=max_predictions)
    for rxnID in pathways.pathways[0].data_frame['equation'].keys():
        print()

def flux_balance_analysis(model, analysis='FBA',
                          result_type='growthrate'):
    '''!
    Function to simulate a model using Flux Balance Analysis (FBA) 
    or FBA-related methods, with Cameo.

    @model String: Model acceptable by Cameo (see 
    http://cameo.bio/02-import-models.html).
    @analysis String: Type of FBA to perform. Allowable types are 
    FBA (standard flux balance analysis) and pFBA (parsimonious 
    FBA). Default value = FBA.
    @result_type String: Type of result to give. Allowable types 
    are growthrate (objective value from FBA) or flux (table of 
    fluxes). Default value = growthrate.
    '''
    import cameo
    _cameo_header()
    print('Load model: %s' % str(model))
    model = cameo.load_model(model)
    if analysis == 'FBA':
        print('Run flux balance analysis on model %s' % str(model))
        result = cameo.fba(model)
    elif analysis =='pFBA':
        print('Run parsimonious flux balance analysis on model %s' \
              % str(model))
        result = cameo.pfba(model)
    if result_type == 'growthrate' and analysis == 'FBA':
        print('Objective value = %s' % \
            abs(result.data_frame.flux).sum())
    if result_type == 'growthrate' and analysis == 'pFBA':
        print('Objective value = %s' % result.objective_value)
    elif result_type == 'flux':
        for metabolite in result.data_frame['flux'].keys():
            print('%s : %s' % \
                (metabolite, 
                 result.data_frame['flux'][metabolite]))
