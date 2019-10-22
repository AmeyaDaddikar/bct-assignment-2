from time import time
import hashlib
import json
import requests
from urllib.parse import urlparse

from account_store import AccountStore

MINER_REWARD    = 20                    # Miner's reward
YAHWEH_ACCOUNT  = 'first account'       # The account that provides miners with coins
MAX_COINS       = 10 ** 9               # Maximum coins with the YAHWEH_ACCOUNT (Total coins that can be mined )


class Blockchain:
    
    def __init__(self):
        
        self.current_transactions = []      # Transactions that are pending to be appended to a block in Blockchain
        self.staged_transactions  = []      # Transactions that are put in a staging area to calculate PoW
        self.chain = []                     # List of Blocks appended in Blockchain
        self.nodes = set()                  # Neighbour full-nodes that can be connected via HTTP
        self.account_store = AccountStore() # AccountStore instance for the current chain in the full node

        ################################################################################################
        ############ GENESIS BLOCK GENERATION ##########################################################
        ################################################################################################


        self.new_transaction(
            sender       ='Let there be light', 
            recipient    = YAHWEH_ACCOUNT, 
            amount       = MAX_COINS, 
            sender_nonce = 1 , 
            isMinerTX    =True
        )
        self.staged_transactions = self.current_transactions   # first block isn't mined per say
        self.current_transactions = []

        self.add_block(previous_hash='1', proof=12)            # Random initial block

        ################################################################################################


    def register_node(self, address):
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError("URL Invalid")

    
    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1



        while current_index < len(chain):
            block = chain[current_index]
            last_block_hash = self.hash(last_block)
            if block['previous_hash'] != last_block_hash:
                return False
            
            if not self.validate(
                last_block['proof'],
                block['proof'], 
                last_block_hash, 
                block['transactions']
            ):
                return False
            
            last_block = block
            current_index += 1
        return True
    
    def update_account_store(self, transactions):

        for tx in transactions:
            self.account_store.transact(
                tx['sender'], 
                tx['recipient'], 
                tx['amount'],
                tx['sender_nonce']
            )
    
    def get_balance(self, address):
        return self.account_store.get_balance(address)


    def resolve_conflicts(self):
        neighbors = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbors:
            url = f'http://{node}/chain'
            response = requests.get(url)

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain  = chain
        
        if new_chain:
            self.chain = new_chain
            return True
        return False


    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]
    
    def new_transaction(self, sender, recipient, amount,sender_nonce, isMinerTX=False):
        ts = {
            "sender"       : sender,
            "recipient"    : recipient,
            "amount"       : amount,
            "sender_nonce" : sender_nonce
        }
        if isMinerTX:
            self.current_transactions.append(ts)
        else:
            self.current_transactions.insert(0, ts)
        
        return self.last_block["index"] + 1
    
    def add_block(self, proof, previous_hash):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": self.staged_transactions,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain[-1])
        }

        self.update_account_store(self.staged_transactions)
        self.staged_transactions = []
        self.chain.append(block)
        return block
    
    @staticmethod
    def validate(last_proof, proof, last_hash, transactions=[]):
        guess = f"{last_proof}{proof}{last_hash}{json.dumps(transactions)}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def mine_proof_of_work(self, last_block, miner_address):

        self.new_transaction(
            sender       = YAHWEH_ACCOUNT,
            recipient    = miner_address,
            amount       = MINER_REWARD,
            sender_nonce = self.account_store.get_account_nonce(YAHWEH_ACCOUNT),
            isMinerTX    = True
        )

        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        self.staged_transactions  = self.current_transactions[:]
        self.current_transactions = []


        proof = 0
        while self.validate(last_proof, proof, last_hash, self.staged_transactions) is False:
            proof += 1
        
        return proof

