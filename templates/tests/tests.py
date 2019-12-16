import sys
sys.path.append('..')
from service.%tabela% import %tabela%Service
from model.%tabela% import %tabela%Model, PK_DEFAULT_VALUE
from util.fake_table import FakeTable
from util.messages import resp_ok, resp_not_found

def test_find_success():
    service = %tabela%Service(FakeTable(%tabela%Model))
    found = service.find(None, [PK_DEFAULT_VALUE])
    assert found

def test_find_failure():
    service = %tabela%Service(FakeTable(%tabela%Model))
    found = service.find(None, [PK_DEFAULT_VALUE])
    assert not found

def test_insert_success():
    table = FakeTable(%tabela%Model)
    service = %tabela%Service(table)
    record = table.default_values()
    status_code = service.insert(record)[1]
    assert status_code == 200

def test_insert_failure():
    service = %tabela%Service(FakeTable(%tabela%Model))
    status_code = service.insert({})[1]
    assert status_code == 400
