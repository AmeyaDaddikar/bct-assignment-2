
import hashlib
import json

class AccountStore:
    def __init__(self):
        """
        __init__ Initializes a store dictionary mapping blockchain addresses to their account
        
        Each expressed in the following format:

        {
            blockchainAddress(string) : {
               'balance': int,
               'nonce'  : int
            }
        }

        the nonce here refers to the Account Nonce, which helps to stop double spending attack
        https://kb.myetherwallet.com/en/transactions/what-is-nonce/

        """
        self.store = {}

    def contains_account(self, address):
        return address in self.store

    def get_balance(self, address):
        if self.contains_account(address) is False:
            return 0
        return self.store[address]['balance']
    
    def get_account_nonce(self, address):
        if self.contains_account(address) is False:
            return -1
        return self.store[address]['nonce']

    def add_account(self, address, amount=0, nonce=0):
        self.store[address] = {
            'balance': amount,
            'nonce'  : nonce
        }
    
    def _deposit(self, address, amount):

        if self.contains_account(address) is False:
            self.add_account(address, amount= amount)

        self.store[address]['balance'] += amount

    def _withdraw(self, address, amount):        
        self.store[address]['balance'] -= amount
    
    def transact(self, sender, recipient, amount, sender_nonce):
        if self.validate_tx(sender, recipient, amount, sender_nonce) is False:
            return False
        
        self._withdraw(sender , amount)
        self._deposit(recipient, amount)
        self.store[sender]['nonce']   += 1


        return True


    def validate_tx(self, sender, recipient, amount, sender_nonce):
        if self.get_balance(sender) < amount:
            return False
        
        stored_nonce = self.get_account_nonce(sender)
        
        return stored_nonce != -1 and stored_nonce == sender_nonce - 1

    def hash_store(self):
        """
        hash_store Returns a SHA256 hash of the self.store
        
        The hash can be used to 
        
        :return: [description]
        :rtype: [type]
        """
        json_store = json.dumps(self.store, sort_keys=True).encode()
        return hashlib.sha256(json_store).hexdigest()
