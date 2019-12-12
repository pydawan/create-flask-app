import sys
sys.path.append('..')
from service.%tabela% import %tabela%Service
from model.%tabela% import %tabela%Model
from util.fake_table import FakeTable
from util.messages import resp_ok, resp_not_found

def test_find_success():
    service = %tabela%Service(
        FakeTable(
            %tabela%Model,
            generate_values=True
        )
    )
    found = service.find(None, [%default%])
    assert found

def test_find_failure():
    service = %tabela%Service(
        FakeTable(
            %tabela%Model,
            generate_values=False
        )
    )
    found = service.find(None, [%default%])
    assert not found

def test_insert_success():
    pass

def test_insert_failure():
    service = %tabela%Service(
        FakeTable(
            %tabela%Model,
            generate_values=False
        )
    )
    status_code = service.insert({})[1]
    assert status_code == 400

def test_update_success():
    pass

def test_update_failure():
    pass

def test_delete_success():
    pass

def test_delete_failure():
    pass
