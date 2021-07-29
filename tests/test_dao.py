import pytest
from brownie import Wei, accounts, Contract, dao

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

def test_add_member(_dao):
    assert _dao.isMember({"from": accounts[1]}) == False
    _dao.addMember(accounts[1], {'from': accounts[8]})
    assert _dao.isMember({"from": accounts[1]}) == True
    assert 1 == 1

def test_fund_deposit(_dao):
    _dao.addMember(accounts[4], {"from": accounts[8]})
    assert _dao.viewInvestment({"from": accounts[4]}) == 0
    _dao.depositFund(1, {"from": accounts[4], "value": "1 ether"})
    assert _dao.viewInvestment({"from": accounts[4]}) == 1

def test_redeem_funds(_dao):
    _dao.addMember(accounts[3], {"from": accounts[8]})
    _dao.depositFund(2, {"from": accounts[3], "value": "2 ether"})
    balance_after_deposit = _dao.contractBalance()
    assert _dao.viewInvestment({"from": accounts[3]}) == 2
    assert balance_after_deposit == _dao.contractBalance()
    _dao.redeemFunds(1, {"from": accounts[3]})
    assert _dao.viewInvestment({"from": accounts[3]}) == 1
    assert _dao.contractBalance() < balance_after_deposit

def test_approve_buyer(_funded_dao):
    assert _funded_dao.viewApprovals(accounts[6], {"from": accounts[5]}) == 0
    _funded_dao.addMember(accounts[5], {"from": accounts[7]})
    _funded_dao.approveBuyer(1, accounts[5], {"from": accounts[6]})
    assert _funded_dao.viewApprovals(accounts[6], {"from": accounts[5]}) == 1