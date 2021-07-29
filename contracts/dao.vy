# @version ^0.2.0

admin: address
endTime: uint256

struct Proposal:
    id: uint256
    name: String[50]
    amount: uint256
    addr: address
    votes: uint256
    end: uint256
    executed: bool

@external
def __init__():
    self.admin = msg.sender
    self.endTime = 1629518400

daoMembers: HashMap[address, bool]
investmentLock: HashMap[address, uint256]
totalDaoTokens: uint256
tokenApprovalLedger: HashMap[address, HashMap[address, uint256]]
proposalCount: uint256
idToProposal: HashMap[uint256, Proposal]
votes: HashMap[address, HashMap[uint256, bool]]

@external
@view
def viewInvestment() -> uint256:
    return self.investmentLock[msg.sender]

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
    # eventually implement an adjusment that will more accurately return ether in relation to current market price
    send(msg.sender, amount)
    return True

# Approve someone to buy your tokens
@external
def approveBuyer(amount: uint256, buyer: address) -> address:
    assert self.investmentLock[msg.sender] > amount, "You can't give approval for more funds than you own"
    assert self.daoMembers[buyer] == True, "You can only grant approval to other members"
    self.tokenApprovalLedger[msg.sender][buyer] += amount
    return buyer

# Buy shares from other members selling (Only after the endTime has passed)
@external
@payable
def buyMemberToken(amount: uint256, seller: address) -> bool:
    assert msg.value >= amount, "You are not sending enough to purchase shares specified"
    assert self.tokenApprovalLedger[seller][msg.sender] > 0, "You have not been approved to purchase from this seller"
    assert self.investmentLock[seller] >= amount, "Seller doesn't have enough to sell to you"
    self.investmentLock[seller] -= amount
    self.investmentLock[msg.sender] += amount
    send(seller, msg.value)
    return True

# Transfer share, any member can give the shares away to any other member
@external
def transferShare(amount: uint256, receiver: address) -> bool:
    assert self.investmentLock[msg.sender] >= amount, "You're trying to transfer more than you have"
    assert self.daoMembers[receiver] == True, "The receiver must also be a DAO member"
    self.investmentLock[msg.sender] -= amount
    self.investmentLock[receiver] += amount
    return True

# Members can create a proposal
@external
@payable
def createProposal(_name: String[50], _amount: uint256, _addr: address) -> Proposal:
    assert self.daoMembers[msg.sender] == True, "Only members can create proposals"
    assert msg.value > 1, "You must spend 1 ether in order to create a proposal"
    new_proposal: Proposal = Proposal({
        id: self.proposalCount,
        name: _name,
        amount: _amount,
        addr: _addr,
        votes: 0,
        # This is one week from block.timestamp
        end: block.timestamp + 604800,
        executed: False
    })
    self.idToProposal[self.proposalCount] = new_proposal
    self.proposalCount += 1
    return new_proposal

# Proposal voting / weighted voting
@external
def proposalVoting(_id: uint256):
    self.idToProposal[_id].votes += 1