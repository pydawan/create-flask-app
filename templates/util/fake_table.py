"""
Objetos para usar como 
mock dos dados de teste (*)
"""

import json

class FakeTable:
    """
    Classe que não é de um banco
    de dados de verdade, mas apenas
    para (*) testes unitários
    """
    def __init__(self, schema):
        self.validator = schema()
        key_list = []
        field_defs = self.validator.declared_fields
        for name in field_defs:
            field = field_defs[name]
            if field.metadata.get('primary_key'):
                key_list.append(name)
        self.key_list = key_list
        self.internal_data = []

    def default_values(self):
        return json.loads(self.validator.dumps(''))

    def insert(self, json):
        errors = self.validator.validate(json)
        if errors:
            return errors
        self.internal_data.append(json)
        return None

    def find_one(self, values):
        for record in self.internal_data:
            match = True
            for field, value in zip(self.key_list, values):
                if record[field] != value:
                    match = False
            if match:
                return record
        return None
