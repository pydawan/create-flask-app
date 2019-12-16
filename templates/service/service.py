import logging
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
    def __init__(self, table=None):
        if table:
            self.table = table
        else:
            self.table = DynamoTable(%tabela%Model, '%tabela%')

    def find(self, params, %campo%=None):
        if %campo%:
            logging.info(f'Procurando "{%campo%}" em %tabela% ...')
            found = self.table.find_one([%campo%])
        else:
            logging.info('Procurando vários registros de %tabela%...')
            found = self.table.find_all(20, self.table.get_conditions(params))
        if not found:
            return resp_not_found()
        return resp_get_ok(found)

    def insert(self, json):
        logging.info('Novo registro será gravado em %tabela%')
        erros = self.table.insert(json)
        if erros:
            return resp_erro(erros)
        return resp_post_ok()

    def update(self, json):
        logging.info('Alterando registro de %tabela%')
        erros = self.table.update(json)
        if erros:
            return resp_erro(erros)
        return resp_ok("objeto atualizado com sucesso")
        
    def delete(self, %campo%):
        logging.info('Excluindo registro de %tabela%')
        self.table.delete(%campo%)
        return resp_ok("objeto deletado com sucesso")
