'''!
Functions to read and process model specifications.

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

class ModelObject(object):
    '''!
    Class to hold an entity (a node) in the model.

    An entity / node contains the following attributes:
        - name: name of this entity (as a string)
        - description: description of this entity (as a string)
        - value: dictionary of values / states where key is the 
        type of value / state and value is the value of the state
        - influx: dictionary of equations describing the inputs 
        into this entity where key is the equation ID and value 
        is the equation
        - outflux: dictionary of equations describing the outputs 
        into this entity where key is the equation ID and value 
        is the equation
    '''
    def __init__(self, name, description=''):
        '''!
        Constructor method.

        @param name String: Name of this entity
        @param description String: Description of this entity
        '''
        self.name = str(name)
        self.description = str(description)
        self.value = {}
        self.influx = {}
        self.outflux = {}
        