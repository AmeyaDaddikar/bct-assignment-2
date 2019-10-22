# BCT Assignment 2
- Ameya Daddikar :: 161070015
- asdaddikar_b16@ce.vjti.ac.in

## Question
>This is a basic framework for a blockchain, and it has some components missing.
Your assignment is to extend the program to include the following features:

- [x] Add a wallet generation script which allows users to create and use wallets.
- [x] Modify the transactions such that each transaction has a wallet address associated with it.
- [x] Create an API where the user can query the blockchain to find out his current wallet balance.


The following repository contains the project that fulfils the above requirements. An additional GUI/CLI can be created for 
the client side to transact with the full nodes.


## My Approach

### Account/Balance Model
It is a fairly simple transaction model as compared to UTXO. Basically it is a dictionary mapping every address to the corresponding 

#### Example
For instance, Alice and Bob want to transact with each other. Alice wants to send Bob 5 tokens and Alice has 10 tokens in her account while Bob has 0. In the account based model, Alice sends Bob 5 tokens which are subtracted from her account and added to Bob’s account. Alice now has 5 tokens and Bob has 5. 

This example was referred from https://bitcoin.stackexchange.com/a/49872

#### Benefits:

##### 1. Simplicity
Ethereum opted for a more intuitive model for the benefit of developers of complex smart contracts, especially those that require state information or involve multiple parties. An example is a smart contract that keeps track of states to perform different tasks based on them. UTXO’s stateless model would force transactions to include state information, and this unnecessarily complicates the design of the contracts.

##### 2. Efficiency 
In addition to simplicity, the Account/Balance Model is more efficient, as each transaction only needs to validate that the sending account has enough balance to pay for the transaction.

#### Account/Balance vs UTXO
The choice between the UTXO model and the balance model is primarily one between privacy incentives and apparent intuitiveness.

If one follows the standard advice of not reusing addresses/outputs/scripts, as to not gratuitously reveal which coins belong to the sender and which belong to the receiver, the two models are actually equivalent. In this case balances would be single use anyway, and there would be as many balances as there would otherwise be UTXOs, removing both the apparent size advantage and convenience.

However, the balance model effectively incentivizes reuse. As the cost to the system (possibly in fees, but certainly in node operation costs) for a balance update is lower than the creation of a new balance, such a system inherently incentives revelation of transaction sources.

### Account Nonce
Every account has a counter called nonce which keeps track on the current transaction number. Every time a client has to transact, he/she has to send the nonce value along with the transaction. Let's see how it helps:

#### Preventing Double Spending Attack
Suppose an address A has 1 ETH.

First, it tries to send 1 ETH to address B. Let's call this transaction A0 because it was signed by A, and it has nonce 0. Now, A tries to double spend this 1 ETH by sending another transaction of 1 ETH to C: let's call it transaction A1. A1 will be rejected immediately by all nodes, because every node can see that A1 must come after A0, and after A0 there isn't enough ETH in A to send A1.

So you can't double-spend with different nonces.

A might try a different strategy: to double spend with the same nonce. First A sends transaction A0 to B, and then it sends another transaction A0 to C. Both have the same nonce, and the same source, but a different destination. Only one of the A0 transactions will be accepted into the blockchain, because all nodes can see that the nonce 0 was used twice by A, and this is not allowed.

So you also can't double-spend with the same nonce.

This example was taken from https://ethereum.stackexchange.com/a/27435

#### Adding additional protection against replay attacks
In my blockchain, say someone tries a Man-In-The-Middle Attack on a client and get hold of his/her transaction request. The Attacker may try to replay the /transaction/new request to overspend the victim's wallet.

However, since for every transaction, a new nonce is required, this means that the next transaction will be signed using a new nonce. Hence the attacker cannot perform the replay attack.

### Code Structure
```
.
├── account_store.py        # AccountStore class that handles the Account/Balance TX model
├── node.py                 # API endpoints to access the full-node
├── chain.py                # The main Blockchain class (contains blocks, consensus, conflict-resolution, etc.)
├── wallet.py               # A Wallet module that helps creation and retrieval of miner/client wallets
├── dependencies.txt        # List of Python Modules and Libraries
├── .gitignore
└── README.md
```

### Miscellaneous design decisions
1. wallet.py has a method save() and restore() to save and retrieve wallets from disk. The key is stored in PEM encrypted format, using the passphrase. So the wallet user needs the passphrase to retrieve these wallets.
2. There is a YAHWEH account which is given all the coins in the Genesis Block. This account in turn rewards the miners. So the Blockchain maintains a limited number of mineable coins in the ecosystem.
3. in Blockchain class in chain.py, self.staged_transactions is added so that once the miner starts mining, the miner focuses on mining the staged_transactions and the rest of the full-node is free to collect the next batch of transactions in current_transactions
```(python)
self.staged_transactions  = self.current_transactions[:]
self.current_transactions = []
```
4. PoW validate() function takes transactions to calculate the new proof. This accounts for integrity of the current transactions as well while mining the current block.
  ```
  def validate(last_proof, proof, last_hash, transactions=[]):
      guess = f"{last_proof}{proof}{last_hash}{json.dumps(transactions)}".encode()
      guess_hash = hashlib.sha256(guess).hexdigest()
      return guess_hash[:4] == "0000"

  ```

5. [AccountStore](account_store.py) is refactored to exist as a separate entity from the Blockchain class.
This is done mainly so that later on when the blockchain encounters neighbouring chains from resolve_conflicts(), the transactions in the obtained chain can be verified by creating a dummy AccountStore instance (dummy_store), traversing block-by-block and updating the dummy_store as per the obtained chain. The dummy_store can verify the transactions if they are valid balance & nonce wise, and only then can the current self.store be replaced with the dummy_store for the full-node.
6. The API call for retrieving the balance was very straight-forward, thanks to refactoring the AccountStore logic and using the Account/Balance model
```
@app.route('/balance', methods=['POST'])
def get_balance():
    address = json.loads(request.data)['address']
    return blockchain.get_balance(address), 200
```





## Libraries
- [Pycryptodome](https://pycryptodome.readthedocs.io)

  A self-contained Python package of low-level cryptographic primitives.

- [Flask](https://flask.palletsprojects.com/en/1.1.x/api/)

  A microframework to run experimental Web Interfaces & APIs

## References
- https://bitcoin.stackexchange.com/
- [Medium's article on UTXO vs Account/Balance Model](https://medium.com/@sunflora98/utxo-vs-account-balance-model-5e6470f4e0cf)
- https://blockonomi.com/utxo-vs-account-based-transaction-models/
- [Account Nonce in Ethereum](https://kb.myetherwallet.com/en/transactions/what-is-nonce/)
