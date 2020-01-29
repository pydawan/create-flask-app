"""
DAO para acesso ao Sql
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from marshmallow.fields import Str

CON_STR = '{dialect}+{driver}://{username}:{password}@{host}:{port}/{database}'

class SqlTable:
    """
    Classe de tabela no Sql
    """
    def __init__(self, schema, table_name, params):
        self.table_name = table_name
        self.validator = schema()
        field_defs = self.validator.declared_fields
        insert_fields = []
        insert_values = []
        update_fields = []
        condition_list = []
        key_list = []
        for field_name in field_defs:
            field = field_defs[field_name]
            if isinstance(field, Str):
                value = "'{"+field_name+"}'"
            else:
                value = "{"+field_name+"}"
            insert_fields.append(field_name)
            if field.metadata.get('primary_key'):
                condition_list.append(
                    '{}={}'.format(
                        field_name,
                        value
                    )
                )
                key_list.append(field_name)
            else:
                update_fields.append(field_name+'='+value)
            insert_values.append(value)
        self.conditions = ' AND '.join(condition_list)
        cmd1 = 'INSERT INTO {}({})VALUES({})'.format(
            table_name,
            ','.join(insert_fields),
            ','.join(insert_values)
        )
        cmd2 = 'UPDATE {} SET {} WHERE {}'.format(
            table_name,
            ','.join(update_fields),
            self.conditions
        )
        self.commands = {
            True: cmd1,
            False: cmd2
        }
        engine = create_engine(
            CON_STR.format(**params)
        )
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.key_list = key_list

    #---- Métodos auxiliares: ----
    def save_data(self, json, is_insert):
        """
        Gravação do registro por insert ou update
        """
        errors = self.validator.validate(json)
        if errors:
            return errors
        json = self.validator.dump(json)
        command = self.commands[is_insert].format(**json)
        self.session.execute(command)
        self.session.commit()
        return None

    #---- Métodos padrão: ----
    def insert(self, json):
        """
        Executa o insert no banco de dados
        """
        return self.save_data(json, True)

    def update(self, json):
        """
        Executa o update no banco de dados
        """
        return self.save_data(json, False)

    def find_all(self, limit=0, filter_expr=''):
        """
        Varre (SCAN) todos os registro da tabela

        filter_expr: expressão `WHERE ...`
        """
        dataset = self.session.execute(
            'SELECT * FROM {} {}'.format(
                self.table_name,
                filter_expr
            )
        )
        result = []
        for row in dataset.fetchall():
            record = {}
            for item in row.items():
                key = item[0]
                value = item[1]
                record[key] = value
            result.append(record)
            if len(result) == limit:
                break
        return result

    def get_conditions(self, values):
        if not isinstance(values, dict):
            result = {}
            if not isinstance(values, list):
                values = [values]
            for key, value in zip(self.key_list, values):
                result[key] = value
            values = result
        return self.conditions.format(**values)

    def find_one(self, values):
        """
        Pesquisa um registro no banco de dados
        """
        return self.find_all(
            0,
            'WHERE {}'.format(
                self.get_conditions(values)
            )
        )[0]

    def delete(self, values):
        """
        Exclui um registro do banco de dados
        """
        self.session.execute(
            'DELETE FROM {} WHERE {}'.format(
                self.table_name,
                self.get_conditions(values)
            )
        )
        self.session.commit()
