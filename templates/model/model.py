from marshmallow import Schema
from marshmallow.fields import Str, Nested, List, Integer, Float, Date
%imports%

PK_DEFAULT_VALUE = %default%

class %tabela%Model(Schema):
    %campo% = %tipo%(primary_key=True, default=PK_DEFAULT_VALUE)
%nested%
