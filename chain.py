from time import time
import hashlib
import json
import requests
from urllib.parse import urlparse


class Blockchain:
    
    def __init__(self):
        self.current_transactions = []   # Transactions that are pending to be appended to a block in Blockchain
        self.chain = []                  # List of Blocks appended in Blockchain
        self.nodes = set()               # Neighbour full-nodes that can be connected via HTTP
        # genesis block
        self.add_block(previous_hash='1', proof=12) # Random initial block
    

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
            
            if not self.validate(last_block['proof'],
                        block['proof'], last_block_hash):
                return False
            last_block = block
            current_index += 1
        return True
    
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
    
    def new_transaction(self, sender, recipient, amount):
        ts = {
            "sender": sender,
            "recipient": recipient,
            "amount": amount
        }
        self.current_transactions.append(ts)
        return self.last_block["index"] + 1
    
    def add_block(self, proof, previous_hash):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": self.current_transactions,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain[-1])
        }

        self.current_transactions = []
        self.chain.append(block)
        return block
    
    @staticmethod
    def validate(last_proof, proof, last_hash):
        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def proof_of_work(self, last_block):
        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        proof = 0
        while self.validate(last_proof, proof, last_hash) is False:
            proof += 1
        
        return proof

