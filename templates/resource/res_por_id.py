from flask_restful import Resource
from service.%tabela% import %tabela%Service

class %tabela%PorId(Resource):
    def get(self, %campo%):
        """
        Faz a pesquisa de %tabela% pelo campo %campo%

        #consulta
        """
        service = %tabela%Service()
        return service.find(None, %campo%)

    def delete(self, %campo%):
        """
        Exclui um registro da tabela %tabela%

        #alteraDados
        """
        service = %tabela%Service()
        return service.delete([%campo%])
