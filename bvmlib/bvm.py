"""
Bayes Vulnerability for Microdata library
=========================================
"""

import numpy
import pandas

class BVM():
    "Bayes Vulnerability for Microdata class dedicated to single-dataset vulnerability assessment."

##### Constructor for single-dataset attacks.

    def __init__(self, dataset):
        "BVM(pandas.DataFrame): Initializes BVM class for single-dataset attacks."
        
        try:
            if type(dataset) is not pandas.DataFrame:
                raise TypeError
            if dataset.empty:
                raise ValueError(dataset)
        
        except TypeError:
            print("The dataset must be a pandas DataFrame.")
        except ValueError:
            print("The dataset cannot be empty.")
        
        else:
            self.dataset = dataset
            self.identifiers = None
            self.quasi_identifiers = None
            self.sensitive_attributes = None

##### Public methods for single-dataset attacks.

    def ids(self, identifiers):
        "self.ids(['id_1',])"
        
        try:
            if type(identifiers) is not list and type(identifiers) is not str:
                raise TypeError
            elif type(identifiers) is str:
                if identifiers not in self.dataset.columns:
                    i = identifiers
                    raise ValueError(identifiers)
            elif type(identifiers) is list:
                for i in identifiers:
                    if type(i) is not str:
                        raise TypeError
                    elif i not in self.dataset.columns:
                        raise ValueError(i)
        
        except TypeError:
            print("A string or a list of strings must be provided.")
        except ValueError:
            print(i, " is not an attribute of the dataset.")
        
        else:
            self.identifiers = identifiers

    def qids(self, quasi_identifiers):
        "self.qids(['quasi_identifier_1','quasi_identifier_2',])"
        
        try:
            if type(quasi_identifiers) is not list and type(quasi_identifiers) is not str:
                raise TypeError
            elif type(quasi_identifiers) is str:
                if quasi_identifiers not in self.dataset.columns:
                    qid = quasi_identifiers
                    raise ValueError(quasi_identifiers)
            elif type(quasi_identifiers) is list:
                for qid in quasi_identifiers:
                    if type(qid) is not str:
                        raise TypeError
                    elif qid not in self.dataset.columns:
                        raise ValueError(qid)
        
        except TypeError:
            print("A string or a list of strings must be provided.")
        except ValueError:
            print(qid, " is not an attribute of the dataset.")
        
        else:
            self.quasi_identifiers = quasi_identifiers

    def sensitive(self, sensitive_attributes):
        "self.sensitive(['sensitive_attribute_1','sensitive_attribute_2',])"
        
        try:
            if type(sensitive_attributes) is not list and type(sensitive_attributes) is not str:
                raise TypeError
            elif type(sensitive_attributes) is str:
                if sensitive_attributes not in self.dataset.columns:
                    s = sensitive_attributes
                    raise ValueError(s)
            elif type(sensitive_attributes) is list:
                for s in sensitive_attributes:
                    if type(s) is not str:
                        raise TypeError
                    elif s not in self.dataset.columns:
                        raise ValueError(s)
        
        except TypeError:
            print("A string or a list of strings must be provided.")
        except ValueError:
            print(s, " is not an attribute of the dataset.")
        
        else:
            self.sensitive_attributes = sensitive_attributes

    def assess(self):
        "self.assess()"
        
        try:
            if self.quasi_identifiers is None:
                raise TypeError
        
        except TypeError:
            print("One or more quasi-identifiers must be assigned.")
        
        else:
            if len(self.quasi_identifiers) > 0:
                "constants --> {sorted_dataset, attributes}"
                "variables --> {re_id, dCR, pCR, bins}"
                "variables --> {re_id, dCR, pCR, bins, att_inf, sensitive_values, CA}"
                constants, variables = self.__setup()
                
                variables = self.__compute(constants, variables)
                
                return variables

##### Private methods for single-dataset attacks.

    def __update_variables(self, variables, eq_class, row):
        "self.__update_variables(self, {re_id, dCR, pCR, bins}, eq_class, row) --> ({re_id, dCR, pCR, bins}, eq_class)"
        "self.__update_variables(self, {re_id, dCR, pCR, bins, att_inf, sensitive_values, CA}, eq_class, row) --> ({re_id, dCR, pCR, bins, att_inf, sensitive_values, CA}, eq_class)"
        # Computes variables['CA'] values from variables['sensitive_values'] and updates variables['CA'].
        
        variables['pCR'] = variables['pCR'] + 1
        class_size_one = False
        
        class_size = sum(variables['sensitive_values'][self.sensitive_attributes[0]].values())
        b = round(100 * 1/class_size)
        variables['bins']['re_id'].update({str(b): variables['bins']['re_id'][str(b)] + class_size})
        
        for attribute in self.sensitive_attributes:
            "counts --> dict_values (dict view, not list) of counts for all possible values of attribute"
            counts = variables['sensitive_values'][attribute].values()
            
            "max_value --> number of entries for the most common value of attribute"
            max_value = max(counts)
            
            "possible_values --> number of possible values for attribute"
            possible_values = len(counts)
            
            try:
                if class_size != sum(counts):
                    raise ValueError(class_size, counts, self.quasi_identifiers, attribute)
            
            except ValueError:
                print("class_size (=" + str(class_size) + ") and counts (=" + str(sum(counts)) + ") error!\n" +
                      "QID: " + str(self.quasi_identifiers) + ". Sensitive attribute: " + attribute + ".")
            
            b = round(100 * max_value/class_size)
            variables['bins'][attribute].update({str(b): variables['bins'][attribute][str(b)] + class_size})
            
            variables['CA'][attribute].update(p = variables['CA'][attribute]['p'] + max_value)
            if possible_values == 1:
                variables['CA'][attribute].update(d = variables['CA'][attribute]['d'] + max_value)
                if max_value == 1:
                    class_size_one = True
            
            # Resets sensitiveValues for given attribute.
            variables['sensitive_values'][attribute].clear()
            
        if class_size_one:
            variables['dCR'] = variables['dCR'] + 1
            try:
                if class_size != 1:
                    raise ValueError(class_size, self.quasi_identifiers)
            
            except ValueError:
                print("class_size (=" + str(class_size) + ") and class_size_one error!\n" +
                      "QID: " + str(self.quasi_identifiers) + ".")
            
        # Updates eq_class to new equivalence class.
        eq_class = row[0:len(self.quasi_identifiers)]
        
        return (variables, eq_class)

    def __compute(self, constants, variables):
        "self.__compute(self, {re_id, dCR, pCR, bins}) --> ({sorted_dataset, attributes}, {re_id, dCR, pCR, bins})"
        "self.__compute(self, {re_id, dCR, pCR, bins, att_inf, sensitive_values, CA}) --> ({sorted_dataset, attributes}, {re_id, dCR, pCR, bins, att_inf, sensitive_values, CA})"
        
        eq_class = ()
        for row in constants['sorted_dataset'][constants['attributes']].itertuples(index=False):
            if eq_class == ():
                eq_class = row[0:len(self.quasi_identifiers)]
            elif row[0:len(self.quasi_identifiers)] != eq_class:
                variables, eq_class = self.__update_variables(variables, eq_class, row)
            
            # Keeps on updating CR values and sensitive_values.
            it = 0
            for attribute in self.sensitive_attributes:
                value = row[len(self.quasi_identifiers)+it]
                if str(value) in variables['sensitive_values'][attribute]:
                    variables['sensitive_values'][attribute].update({str(value): variables['sensitive_values'][attribute][str(value)] + 1})
                else:
                    variables['sensitive_values'][attribute].update({str(value): 1})
                it += 1
        
        # For accounting for the last equivalence class.
        variables, eq_class = self.__update_variables(variables, eq_class, row)
        
        dataset_size = constants['sorted_dataset'].shape[0]
        
        if dataset_size == 1:
            variables['dCR'] = (variables['dCR']/dataset_size) - 1
        else:
            variables['dCR'] = variables['dCR']/dataset_size
        
        for case in self.sensitive_attributes + ['re_id']:
            for i in range(101):
                variables['bins'][case].update({str(i): variables['bins'][case][str(i)]/dataset_size})
        
        d = {'QID': str(self.quasi_identifiers), 'dCR': variables['dCR'], 'pCR': variables['pCR'], 'Prior': 1/dataset_size,
             'Posterior': variables['pCR']/dataset_size, 'Histogram': str(variables['bins']['re_id'])}
        variables['re_id'] = pandas.concat([variables['re_id'], pandas.DataFrame(data = d, index=[0])], ignore_index = True)
        
        for attribute in self.sensitive_attributes:
            variables['CA'][attribute].update(d = variables['CA'][attribute]['d']/dataset_size)
            
            if variables['CA'][attribute]['d'] == 1:
                variables['CA'][attribute].update(d = variables['CA'][attribute]['d'] - 1)
            
            most_probable_count = constants['sorted_dataset'].groupby(attribute).size().max()
            
            variables['CA'][attribute].update(p = variables['CA'][attribute]['p']/most_probable_count)
            
            d = {'QID': str(self.quasi_identifiers), 'Sensitive': attribute, 'dCA': variables['CA'][attribute]['d'],
                 'pCA': variables['CA'][attribute]['p'], 'Prior': most_probable_count/dataset_size,
                 'Posterior': (variables['CA'][attribute]['p'] * most_probable_count)/dataset_size,
                 'Histogram': str(variables['bins'][attribute])}
            variables['att_inf'] = pandas.concat([variables['att_inf'], pandas.DataFrame(data = d, index=[0])],
                                                 ignore_index = True)
        
        return variables

    def __setup(self):
        "self.__setup() --> ({sorted_dataset, attributes}, {re_id, dCR, pCR, bins})"
        "self.__setup() --> ({sorted_dataset, attributes}, {re_id, dCR, pCR, bins, att_inf, sensitive_values, CA})"
        
        sorted_dataset = self.dataset.sort_values(by=self.quasi_identifiers, axis='index', inplace=False, kind='mergesort')
        
        re_id = pandas.DataFrame(columns=['QID', 'dCR', 'pCR', 'Prior', 'Posterior', 'Histogram'])
        
        dCR = 0
        pCR = 0
        
        "bins --> {'re_id':{'0%':a,'1%':b,'2%':c,...,'100%':d},}"
        "bins --> {'re_id':{'0%':a,'1%':b,'2%':c,...,'100%':d},'attr_1':{'0%':e,...,'100%':f},}"
        "bins: 'x%' for chance of re-identification or attribute-inference, y% for amount of rows with 'x%' chance"
        bins = {}
        bins['re_id'] = {}
        for i in range(101):
            bins['re_id'].update({str(i): 0})
        
        "attributes --> self.quasi_identifiers"
        "attributes --> self.quasi_identifiers + self.sensitive_attributes"
        attributes = self.quasi_identifiers.copy()
        
        if self.sensitive_attributes is not None:
            att_inf = pandas.DataFrame(columns=['QID', 'Sensitive', 'dCA', 'pCA', 'Prior', 'Posterior', 'Histogram'])
            
            "sensitive_values --> {'attr_1':{'val_1':count_1,'val_2':count_2},'attr_2':{'val_1':count_1},}"
            "sensitive_values: attr_i from self.sensitive_attributes, val_j from attr_i, count_k from val_j"
            sensitive_values = {}
            
            "CA --> {'attr_1':{'d':x,'p':y},'attr_2':{'d':a,'p':b},}"
            "CA: attr_i from self.sensitive_attributes, 'd' for dCA value, 'p' for pCA value"
            CA = {}
            
            for attribute in self.sensitive_attributes:
                sensitive_values[attribute] = {}
                CA[attribute] = {'d': 0,'p': 0}
                bins[attribute] = {}
                for i in range(101):
                    bins[attribute].update({str(i): 0})
                attributes.append(attribute)
            
            return ({'sorted_dataset': sorted_dataset, 'attributes': attributes},
                    {'re_id': re_id, 'dCR': dCR, 'pCR': pCR, 'bins': bins, 'att_inf': att_inf,
                     'sensitive_values': sensitive_values, 'CA': CA})
        else:
            return ({'sorted_dataset': sorted_dataset, 'attributes': attributes},
                    {'re_id': re_id, 'dCR': dCR, 'pCR': pCR, 'bins': bins,})