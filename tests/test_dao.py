import pytest
from brownie import Wei, ZERO_ADDRESS, accounts, Contract, dao



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

    original_contract_balance = _funded_dao.contractBalance()
    original_member_balance = _funded_dao.viewInvestment({"from": accounts[6]})
    _funded_dao.buyMemberToken(1, accounts[6], {"from": accounts[5], "value": "1 ether"})
    assert _funded_dao.viewInvestment({"from": accounts[5]}) == 1
    assert original_contract_balance == _funded_dao.contractBalance()
    assert original_member_balance > _funded_dao.viewInvestment({"from": accounts[6]})

def test_transfer_share(_funded_dao2, frog, toad):
    _funded_dao2.addMember(accounts[2], {"from": frog})
    assert _funded_dao2.viewInvestment({"from": accounts[2]}) == 0
    _funded_dao2.transferShare(1, accounts[2], {"from": toad})
    assert _funded_dao2.viewInvestment({"from":accounts[2]}) == 1

def test_create_proposal(_funded_dao2, frog, toad):
    new_proposal_id = _funded_dao2.createProposal("Dao proposal #1", 1, accounts[9], {"from": toad, "value": "1 ether"})
    assert new_proposal_id.events[0]['name'] == "Dao proposal #1"
    _funded_dao2.addMember(accounts[2], {"from": frog})
    _funded_dao2.depositFund(1, {"from": accounts[2], "value": "1 ether"})
    member_vote = _funded_dao2.proposalVoting(new_proposal_id.events[0]['id'], {"from": accounts[2]})
    #check Proposal votes should be 1, since that's how much the one person who voted had
    assert member_vote.events[0]['amount'] == 1

# Needs fixing and figuring out how to properly simulate block.timestamp in the future

# def test_vote_check_and_execution(_funded_dao3, alligator, crocodile):
#     new_proposal = _funded_dao3.createProposal("Dao Proposal #2", 1, accounts[9], {"from": crocodile, "value": "1 ether"})
#     _funded_dao3.proposalVoting(new_proposal.events[0]["id"], {"from": crocodile})
#     assert _funded_dao3.checkVotes(new_proposal.events[0]["id"], {"from": alligator}) == True

# def test_return_profit(_dao):
#     _dao.returnProfit()