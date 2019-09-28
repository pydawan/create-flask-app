import json
from flask_restful import Resource
from flask import request, jsonify
from service.%tabela% import %tabela%Service

class Todos%tabela%s(Resource):
    def get(self):
        """
        Traz todos os registros da tabela %tabela%

        #consulta
        """
        service = %tabela%Service()
        return service.find(request.args)
    
    def post(self):
        """
        Grava um novo registro em %tabela%

        #alteraDados
        """
        req_data = request.get_json()
        service = %tabela%Service()
        return service.insert(req_data)

    def put(self):
        """
        Alterar os dados de um registro de %tabela%

        #alteraDados
        """
        req_data = json.loads(request.data.decode("utf8"))
        service = %tabela%Service()
        return service.update(req_data)
