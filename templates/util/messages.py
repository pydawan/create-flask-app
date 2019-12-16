import datetime
import logging

def resp_ok(msg="OK", data=None, status_code=200):
    result = {}
    result['timeStamp'] = str(datetime.datetime.now())
    if data:
        result['dados'] = data
    result['status'] = msg
    logging.info(msg)
    return result, status_code

def resp_erro(msg, status_code=400):
    result = {}
    result['timeStamp'] = str(datetime.datetime.now())
    result['status'] = msg
    logging.error(f'Erro {status_code}: {msg}')
    return result, status_code

def resp_not_found(msg="O recurso não foi encontrado"):
    return resp_erro(msg, 404)

def resp_get_ok(data=None):
    return resp_ok('objeto recuperado com sucesso', data)

def resp_post_ok(data=None):
    return resp_ok('Recurso criado com sucessso', data, 201)
