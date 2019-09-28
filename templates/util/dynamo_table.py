import os
import json
import decimal
import boto3
from datetime import datetime
from flask import current_app
from botocore.exceptions import ClientError, ValidationError
from boto3.dynamodb.conditions import Key, Attr
from marshmallow.fields import Integer, Float, Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)

class DynamoTable:

    existing = []

    def __init__(self, schema, table_name, local_connection=True):
        self.validator = schema()
        map_dict = {}
        key_list = []
        field_defs = self.validator.declared_fields
        for name in field_defs:
            field = field_defs[name]
            if field.metadata.get('primary_key'):
                key_list.append(name)
            is_integer = isinstance(field, Integer)
            is_float = isinstance(field, Float)
            is_decimal = isinstance(field, Decimal)
            if is_integer or is_float or is_decimal:
                map_dict[name] = "N"
            else:
                map_dict[name] = "S"
        self.table_name = table_name
        self.key_list = key_list
        self.map = map_dict
        if local_connection:
            self.connection = boto3.resource(
                'dynamodb',
                region_name='us-west-2',
                endpoint_url="http://localhost:8000",
                aws_access_key_id="",
                aws_secret_access_key=""
            )
        else:
            self.connection = boto3.resource('dynamodb')
        self.table_exists = table_name in DynamoTable.existing
        if not self.table_exists:
            try:
                self.table = self.create_table()
            except (ClientError, os.error):
                self.table_exists = True
        if self.table_exists:
            self.table = self.connection.Table(self.table_name)
        DynamoTable.existing.append(table_name)

    def create_table(self):
        kschema = []
        k_type = 'HASH'
        definitions = []
        for key in self.key_list:
            kschema.append({'AttributeName': key, 'KeyType': k_type})
            k_type = 'RANGE'
            attr_type = self.map.get(key) or 'S'
            definitions.append({'AttributeName': key, 'AttributeType': attr_type})
        return self.connection.create_table(
            TableName=self.table_name,
            KeySchema=kschema,
            AttributeDefinitions=definitions,
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            })

    def get_key_expr(self, dataset):
        expression = 'SET '
        key_fields = {}
        attributes = {}
        for field in self.map:
            value = dataset.get(field)
            if not value:
                continue
            if field in self.key_list:
                key_fields[field] = value
                continue
            param_name = ':p_{}'.format(field)
            if attributes:
                expression += ', '
            expression += f'{field} = {param_name}'
            attributes[param_name] = value
        return key_fields, expression, attributes

    def insert(self, json):
        errors = self.validator.validate(json)
        if errors:
            return errors
        today = datetime.today()
        json['dtInclusao'] = str(today)
        self.table.put_item(
            Item=json
        )
        return None

    def update(self, json):
        today = datetime.today()
        json['dtAlteracao'] = str(today)
        key_fields, expression, attributes = self.get_key_expr(json)
        try:
            self.table.update_item(
                Key=key_fields,
                UpdateExpression=expression,
                ExpressionAttributeValues=attributes,
                ReturnValues="UPDATED_NEW"
            )
        except (ClientError, ValidationError) as update_error:
            return str(update_error)
        return None

    def find_all(self, limit=None, filter=None):
        params = {}
        if limit:
            params['Limit'] = limit
        if filter:
            params['FilterExpression'] = filter
        result = self.table.scan(**params)
        result = json.loads(json.dumps(result, cls=DecimalEncoder))
        if result.get('Count'):
            return result.get('Items')
        return None

    def find_one(self, values):
        result = self.table.query(
            KeyConditionExpression=self.get_conditions(values)
        )
        result = json.loads(json.dumps(result, cls=DecimalEncoder))
        if result.get('Count'):
            return result.get('Items')[0]
        return None

    def delete(self, values):
        if isinstance(values, dict):
            key_expr = values
        else:
            key_expr = {}
            if not isinstance(values, list):
                values = [values]
            for field, value in zip(self.key_list, values or []):
                key_expr[field] = value
        self.table.delete_item(Key=key_expr)

    def get_conditions(self, values):
        conditions = []
        is_filter = isinstance(values, dict)
        if is_filter:
            for field in values:
                value = values[field]
                conditions.append(
                    Attr(field).eq(value)
                )
        elif values:
            for field, value in zip(self.key_list, values or []):
                conditions.append(
                    Key(field).eq(value)
                )
        result = None
        for condition in conditions:
            if result:
                result = result & condition
            else:
                result = condition
        return result

    @staticmethod
    def get_filter_text(field, value):
        return  Attr(field).contains(value)

    @staticmethod
    def get_filter_values(field, value1, value2):
        return Attr(field).between(
            value1,
            value2
        )
