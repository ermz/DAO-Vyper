# @version ^0.2.0

admin: address
endTime: uint256

@external
def __init__():
    self.admin = msg.sender
    self.endTime = 1629518400

daoMembers: HashMap[address, bool]
investmentLock: HashMap[address, uint256]
totalDaoTokens: uint256
tokenApprovalLedger: HashMap[address, HashMap[address, uint256]]

@external
def addMember(member: address) -> bool:
    assert msg.sender == self.admin, "Only the admin may add new members"
    assert self.daoMembers[msg.sender] == False, "You are already a member, don't get greedy"
    self.daoMembers[msg.sender] = True
    return True

# The contract needs to mint a certain amount everytime an investore deposits
@internal
def daoMint(depositor: address, amount: uint256) -> address:
    self.totalDaoTokens += amount
    return depositor

@external
@payable
def depositFund(amount: uint256) -> bool:
    assert self.daoMembers[msg.sender] == True, "You must be a member"
    assert msg.value >= amount, "Insufficient funds"
    assert block.timestamp > self.endTime, "It's too late to deposit funds"
    assert self.investmentLock[msg.sender] == 0, "You can't deposit multiple times"

    self.investmentLock[msg.sender] = amount
    self.daoMint(msg.sender, amount)
    return True

# First a way for investors to cash out, before the end of investing period
@external
@payable
def redeemFunds(amount: uint256) -> bool:
    assert self.balance > amount, "There isn't enough ether in the smart contract"
    assert amount <= self.investmentLock[msg.sender], "You're trying to redeem more than you have"
    assert self.endTime > block.timestamp, "You're time has run out, you can still sell to other members"
    self.investmentLock[msg.sender] -= amount
    self.totalDaoTokens -= amount
    return True

# Approve someone to buy your tokens
@external
def approveBuyer(amount: uint256, buyer: address) -> address:
    assert self.investmentLock[msg.sender] > amount, "You can't give approval for more funds than you own"
    assert self.daoMembers[buyer] == True, "You can only grant approval to other members"
    self.tokenApprovalLedger[msg.sender][buyer] += amount
    return buyer
