'''
Genome-Scale Model to Kinetic Model Converter

Date created: 20th May 2021

Authors: Nabil Amir-Hamzah, Zhi Jue Kuan, Maurice HT Ling

This file is part of AdvanceSynModeller, which is a part of 
AdvanceSynToolKit.

Copyright (c) 2018, AdvanceSyn Private Limited and authors.

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

import pandas as pd

def gsm_km_converter(input_model, input_name, outputfile, rxnList, 
                     metabolite_initial, enzyme_conc, enzyme_kcat, enzyme_km):
    pd.set_option('display.max_colwidth', None)
    filenamedata = []
    filenamedata.append(outputfile)
    filenamedata = [item.replace(" ", "_") for item in filenamedata]
    filename = ''.join(map(str, filenamedata))

    df = pd.DataFrame(rxnList)
    df.columns = ['rxn_no', 'rxn_id', 'reactants', 'products', 'rxn_name']
    df = df.applymap(str)
    df.style.hide_index()
    df['reactants'] = df['reactants'].str.replace("[", "", regex=False)
    df['reactants'] = df['reactants'].str.replace("']", "", regex=False)
    df['reactants'] = df['reactants'].str.replace("]", "", regex=False)
    df['reactants'] = df['reactants'].str.replace("', '", " + m_", regex=False)
    df['reactants'] = df['reactants'].str.replace("'", "m_", regex=False)

    df['products'] = df['products'].str.replace("[", "", regex=False)
    df['products'] = df['products'].str.replace("']", "", regex=False)
    df['products'] = df['products'].str.replace("]", "", regex=False)
    df['products'] = df['products'].str.replace("', '", " + m_", regex=False)
    df['products'] = df['products'].str.replace("'", "m_", regex=False)

    df['rxn_id'] = 'm_' + df['rxn_id']

    #Objects List, df2 & 3
    df2 = pd.DataFrame()
    df2['obj'] = df['products']
    df2 = df2.drop('obj', axis=1).join(df2['obj'].str.split('+', 
        expand= True).stack().reset_index(level=1, 
        drop= True).rename('obj').str.replace(" ", "", regex=False))
    df3 = pd.DataFrame()
    df3['obj'] = df['reactants']
    df3 = df3.drop('obj', axis=1).join(df3['obj'].str.split('+', 
        expand= True).stack().reset_index(level=1, 
        drop= True).rename('obj').str.replace(" ", "", regex=False))
    df4 = pd.concat([df2, df3], ignore_index= True)
    df4 = df4.astype('str')
    df4 = df4.drop_duplicates()
    df4 = df4[df4.obj != '']
    df4 = df4.reset_index(drop= True)

    #reactions
    df['rxn_list'] = ('R' + df['rxn_no'] + ': ' + '' + \
        df['reactants'] + ' -> ' + '' + df['products'] + '')
    df['rate_law'] = ('(${Variables:' + df['rxn_id'] + '_kcat}' + \
        ' * ' + '${Variables:' + df['rxn_id'] + '_conc}' +  \
        ' * ' + df['reactants'].str.replace("+", "*", regex= False) + \
        ')/' + '(${Variables:' + df['rxn_id'] + '_km}' + \
        ' + ' + '${Variables:' + df['rxn_id'] + '_conc}' +  \
        ' * ' + df['reactants'].str.replace("+", "*", regex= False) + ')')

    outputList = ['[Specification]', '\n', 'type : 1', '\n\n',
                  '[Identifiers]', '\n', 'name : ' + input_model, '\n', 
                  'author : ' + input_name, '\n\n']
    objectList = ['[Objects]' + '\n'] + \
        [row['obj'].strip() + ' : ' + row['obj'].strip() + '\n' 
        for index, row in df4.iterrows()] + \
        ['\n\n']

    initialsList = ['[Initials]' + '\n'] + \
        [row['obj'].strip() + ' : ' + str(metabolite_initial) + '\n' 
        for index, row in df4.iterrows()] + \
        ['\n\n']

    variable_concList = ['[Variables]' + '\n'] + \
        [row['rxn_id'].strip() + '_conc : ' + str(enzyme_conc) + '\n' 
        for index, row in df.iterrows()]

    variable_kcatList = [row['rxn_id'].strip() + '_kcat : ' + str(enzyme_kcat) + '\n' 
                         for index, row in df.iterrows()]

    variable_kmList = [row['rxn_id'].strip() + '_km : ' + str(enzyme_km) +'\n' 
                       for index, row in df.iterrows()] + ['\n\n']

    reactionList = ['[Reactions]' + '\n'] + \
        [row['rxn_list'].strip() +  ' | ' + row['rate_law'].strip() + '\n' 
        for index, row in df.iterrows()]

    outputList = outputList + objectList + initialsList + \
                 variable_concList + variable_kcatList + \
                 variable_kmList + reactionList

    #write to file
    file = open(filename, 'w')
    file.writelines(outputList)
    file.close()

