from model.%tabela% import %tabela%Model
from util.dynamo_table import DynamoTable
from util.messages import (
    resp_erro,
    resp_not_found,
    resp_post_ok,
    resp_get_ok,
    resp_ok
)

class %tabela%Service:
    def __init__(self):
        self.table = DynamoTable(%tabela%Model, '%tabela%')

    def find(self, params, %campo%=None):
        if %campo%:
            found = self.table.find_one([%campo%])
        else:
            found = self.table.find_all(20, self.table.get_conditions(params))
        if not found:
            return resp_not_found()
        return resp_get_ok(found)

    def insert(self, json):
        erros = self.table.insert(json)
        if erros:
            return resp_erro(erros)
        return resp_post_ok()

    def update(self, json):
        erros = self.table.update(json)
        if erros:
            return resp_erro(erros)
        return resp_ok("objeto atualizado com sucesso")
        
    def delete(self, %campo%):
        self.table.delete(%campo%)
        return resp_ok("objeto deletado com sucesso")
