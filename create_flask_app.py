import os
import sys
import json
import shutil

def renderiza(pasta, arquivo, params, gravar=True):
        if isinstance(arquivo, list):
                origem = os.path.join('templates', pasta, arquivo[0])
        else:
                origem = os.path.join('templates', pasta, arquivo)
        with open(origem, 'r') as f:
                texto = f.read()
                f.close()
        for key in params:
                value = params[key]
                if not isinstance(value, str):
                        continue
                texto = texto.replace(f'%{key}%', value)
        if gravar:
                if not pasta:
                        destino = params["nome_API"]
                else:
                        destino = os.path.join(params["nome_API"], pasta)
                if not os.path.exists(destino):
                        os.makedirs(destino)
                        init_file = os.path.join(
                                destino,
                                '__init__.py'
                        )
                        with open(init_file, 'w') as f:
                                f.write(' ')
                                f.close()
                if isinstance(arquivo, list):
                        destino = os.path.join(destino, arquivo[1])
                else:
                        destino = os.path.join(destino, arquivo)
                with open(destino, 'w') as f:
                        f.write(texto)
                        f.close()
        return texto

def copy_util(dst, ignorar):
        src = os.path.join('templates', 'util')
        dst = os.path.join(dst, 'util')
        os.makedirs(dst)
        for info in os.listdir(src):
                if info == ignorar:
                        continue
                s = os.path.join(src, info)
                d = os.path.join(dst, info)
                shutil.copy2(s, d)
                print('/', end='')

def field_type(field):
        types = {
                'nm': ('Str', "12"),
                'tx': ('Str', "121"),
                'id': ('Str', "1212"),
                'nr': ('Integer', 1212),
                'in': ('Boolean', False),
                'vl': ('Float', 12.12),
                'dt': ('Date', '"2019-12-12"'),
        }
        result = types.get(
                field[:2], ('Str','"???"')
        )
        return result

def carrega_json(arquivo):
        with open(arquivo, 'r') as f:
                texto = f.read()
                f.close()
        result = json.loads(texto)
        return result['tabelas'], result.get('db_config')

def exec_cmd():
        if len(sys.argv) < 2:
                print("""
                *** Create-Flask-App ***

                Uso:
                > python create_flask_app.py <arquivo Json>

                Exemplo:
                > python create_flask_app.py Filmes
                """)
                return
        arquivo = os.path.splitext(sys.argv[1])[0]
        tabelas, config_sql = carrega_json(arquivo + '.json')
        print('-'*50)
        print('tabelas = ', tabelas)
        print('config_sql = ', config_sql)
        print('-'*50)
        resumo = {}
        resumo['nome_API'] = sys.argv[1]
        for info in tabelas:
                info['nome_API'] = sys.argv[1]
                if 'campo' not in info:
                        info['campo'] = 'id'
                info['tipo'], info['default'] = field_type(info['campo'])
                print('*', end = '')
                for template in ['config_routes', 'imports', 'swagger_details']:
                        texto = resumo.get(template, '')
                        resumo[template] = texto + renderiza(
                                'app',
                                f'{template}.py',
                                info,
                                False
                        )
                        print('+', end = '')
                for template in ['model', 'resource', 'service', 'tests']:
                        lista_nested = info.get('nested', [])
                        modulo = info['tabela']
                        if template == 'resource':
                                for sub in ['res_por_id.py', 'todos_res.py']:
                                        if sub[:4] == 'todo':
                                                modulo += 's'
                                        renderiza(
                                                template,
                                                [
                                                        sub,
                                                        sub.replace('res', modulo)
                                                ],
                                                info
                                        )
                                continue
                        elif template == 'service':
                                if config_sql:
                                        info['import_classe_dados'] = 'sql_table'
                                        info['classe_dados'] = 'SqlTable'
                                        info['extra'] = str(config_sql)
                                else:
                                        info['import_classe_dados'] = 'dynamo_table'
                                        info['classe_dados'] = 'DynamoTable'
                                        info['extra'] = 'True'
                        elif template == 'model':
                                imports = ''
                                atribuicoes = ''
                                for nested in lista_nested:
                                        imports += f'from model.{nested} import {nested}Model\n'
                                        atribuicoes += f'    {nested.lower()} = Nested({nested}Model)\n'
                                info['imports'] = imports
                                info['nested'] = atribuicoes
                        elif template == 'tests':
                                modulo = 'test_' + modulo
                        renderiza(
                                template,
                                [
                                        f'{template}.py',
                                        f"{modulo}.py"
                                ],
                                info
                        )
                        print('.', end = '')
        renderiza('', 'app.py', resumo)
        if config_sql:
                copy_util(arquivo, 'dynamo_table.py')
        else:
                copy_util(arquivo, 'sql_table.py')
        print('='*50)
        print('\tOperação Concluída!')
        print('-'*100)

exec_cmd()
