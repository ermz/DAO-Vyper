import pytest
from brownie import accounts, Contract, dao

@pytest.fixture
def _dao():
    _dao = dao.deploy({'from': accounts[8]})
    return _dao

@pytest.fixture
def _funded_dao():
    _funded_dao = dao.deploy({'from': accounts[7]})
    _funded_dao.addMember(accounts[6], {"from": accounts[7]})
    _funded_dao.depositFund(2, {"from": accounts[6], "value": "2 ether"})
    return _funded_dao

@pytest.fixture()
def frog(accounts):
    return accounts[0]

@pytest.fixture()
def toad(accounts):
    return accounts[3]

@pytest.fixture()
def _funded_dao2(frog, toad):
    _funded_dao2 = dao.deploy({"from": frog})
    _funded_dao2.addMember(toad, {"from": frog})
    _funded_dao2.depositFund(2, {"from": toad, "value": "2 ether"})
    return _funded_dao2

@pytest.fixture()
def alligator(accounts):
    return accounts[5]

@pytest.fixture()
def crocodile(accounts):
    return accounts[6]

@pytest.fixture
def _funded_dao3(alligator, crocodile):
    _funded_dao3 = dao.deploy({"from": alligator})
    _funded_dao3.addMember(crocodile, {"from": alligator})
    _funded_dao3.depositFund(3, {"from": crocodile, "value": "3 ether"})
    return _funded_dao3