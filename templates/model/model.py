from marshmallow import Schema
from marshmallow.fields import Str, Nested, List, Integer, Float, Date
%imports%

class %tabela%Model(Schema):
    %campo% = %tipo%(primary_key=True, default=%default%)
%nested%
