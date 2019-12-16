import os
import sys
import shutil

def extrai_info(expr, parent=None):
        result = []
        item = ''
        if not parent:
                expr += ','
        obj_dados = None
        while expr:
                char = expr[0]
                expr = expr[1:]
                if char in ['[', ']', ',']:
                        if item:
                                item = item.strip()
                                if item[0] == '/':
                                        nome_tabela = (
                                                item[1].upper()+
                                                item[2:].lower().replace('-', '_')
                                        )
                                        obj_dados = {
                                                'tabela':  nome_tabela
                                        }
                                        if parent:
                                                lista_nested = parent.setdefault(
                                                        'nested', []
                                                )
                                                lista_nested.append(nome_tabela)
                                                parent['nested'] = lista_nested
                                        result.append(obj_dados)
                                elif parent:
                                        parent['campo'] = item
                                item = ''
                        if char == '[':
                                sub, expr = extrai_info(expr, obj_dados)
                                if not sub:
                                        continue
                                result += sub
                        elif char == ']' and parent:
                                break
                else:
                        item += char
        return result, expr

def grava_template(pasta, arquivo, params, gravar=True):
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

def copy_util(dst):
        src = os.path.join('templates', 'util')
        dst = os.path.join(dst, 'util')
        os.makedirs(dst)
        for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(dst, item)
                shutil.copy2(s, d)
                print('/', end='')

def field_type(field):
        types = {
                'nm': {
                        "type":'Str',
                        "default": "12"
                },
                'tx': {
                        "type":'Str',
                        "default": "121"
                },
                'id': {
                        "type":'Str',
                        "default": "1212"
                },
                'nr': {
                        "type":'Integer',
                        "default": 1212
                },
                'in': {
                        "type":'Boolean',
                        "default": False
                },
                'vl': {
                        "type":'Float',
                        "default": 12.12
                },
                'dt': {
                        "type":'Date',
                        "default": '"2019-12-12"'
                }
        }
        result = types.get(
                field[:2],
                {
                        "type": 'Str',
                        "default": '"???"'
                }
        )
        return result['type'], result['default']

def exec_cmd():
        if len(sys.argv) < 3:
                print("""
                *** Create-Flask-App ***

                Uso:
                > python create_flask_app.py <nome-API> +<rota>[dominio...]

                Exemplo:
                > python create_flask_app.py Pessoa +cliente[+genero,+documento[nmCpf]+financeiro[nrConta]]+faixa[vlMinimo]+evento[dtEvento]
                """)
                return
        cmd = sys.argv[2].replace('+', '/')
        info = extrai_info(cmd)[0]
        app_parts = {}
        app_parts['nome_API'] = sys.argv[1]
        for item in info:
                item['nome_API'] = sys.argv[1]
                if 'campo' not in item:
                        item['campo'] = 'id'
                item['tipo'], item['default'] = field_type(item['campo'])
                print('*', end = '')
                for part in ['config_routes', 'imports', 'swagger_details']:
                        content = app_parts.get(part, '')
                        app_parts[part] = content + grava_template(
                                'app',
                                f'{part}.py',
                                item,
                                False
                        )
                        print('+', end = '')
                for part in ['model', 'resource', 'service', 'tests']:
                        lista_nested = item.get('nested', [])
                        file_name = item['tabela']
                        if part == 'resource':
                                for sub in ['res_por_id.py', 'todos_res.py']:
                                        if sub[:4] == 'todo':
                                                file_name += 's'
                                        target = sub.replace('res', file_name)
                                        grava_template(
                                                part,
                                                [sub, target],
                                                item
                                        )
                                continue
                        elif part == 'model':
                                imports = ''
                                tabelas = ''
                                for nested in lista_nested:
                                        imports += f'from model.{nested} import {nested}Model\n'
                                        tabelas += f'    {nested.lower()} = Nested({nested}Model)\n'
                                item['imports'] = imports
                                item['nested'] = tabelas
                        elif part == 'tests':
                                file_name = 'test_' + file_name
                        grava_template(
                                part,
                                [
                                        f'{part}.py',
                                        f"{file_name}.py"
                                ],
                                item
                        )
                        print('.', end = '')
        grava_template('', 'app.py', app_parts)
        copy_util(sys.argv[1])
        print('='*50)
        print('\tOperação Concluída!')
        print('-'*100)

exec_cmd()
