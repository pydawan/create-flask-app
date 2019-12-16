# -*- coding: utf-8 -*-
import logging
from flask import Flask, Blueprint, jsonify
from flask_restful import Api
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from util.swagger_generator import FlaskSwaggerGenerator
%imports%

BASE_PATH = '/%nome_API%'

def config_routes(app):
    api = Api(app)
    #--- Resources: ----
%config_routes%    
    #-------------------

def set_swagger(app):
    swagger_url = '/docs'
    swaggerui_blueprint = get_swaggerui_blueprint(
        swagger_url,
        '/api',
        config={
            'app_name': "*- %nome_API% -*"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=swagger_url)


def swagger_details(args):
    id_route = args[0]
    params = args[1]
    model = None
    resource = None
    docstring = ""
    if id_route == 'docs':
        docstring = """Documentação no formato Swagger
        #documentação
        """
%swagger_details%    
    ignore = False
    return model, resource, docstring, ignore

logging.basicConfig(
    filename='%nome_API%.log',
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

APP = Flask(__name__)
CORS(APP)
config_routes(APP)
set_swagger(APP)

@APP.route('/api')
def get_api():
    """
    Json com os dados da Api

    #documentação
    """
    generator = FlaskSwaggerGenerator(
        swagger_details
    )
    return jsonify(generator.content)

if __name__ == '__main__':
    APP.run()
