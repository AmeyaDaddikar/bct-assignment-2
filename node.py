from uuid import uuid4
import json
from flask import Flask, jsonify, request
from chain import Blockchain

app = Flask(__name__)

node_identifier = str(uuid4()).replace('-','')

blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    blockchain.new_transaction(
        sender='0',
        recipient=node_identifier,
        amount=20
        )
    previous_hash = blockchain.hash(last_block)
    block = blockchain.add_block(proof, 
                        previous_hash)
    
    response = {
        "message": "Block is created",
        "index": block['index'],
        "transactions": block['transactions'],
        "proof": block['proof'],
        "previous_hash" : block['previous_hash']
    }

    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    required = ['sender', 'recipient', 'amount']

    if not all(k in values for k in required):
        return 'Missing Values', 400
    
    sender = values['sender']
    recipient = values['recipient']
    amount = values['amount']
    index = blockchain.new_transaction(sender,
                        recipient,amount)
    
    response = {
        'message': f'Block #{index}'
        }
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        "chain": blockchain.chain,
        "length": len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = json.loads(request.data)
    nodes = values.get('nodes')

    if nodes is None:
        return 'Error', 400
    
    for node in nodes:
        blockchain.register_node(
            "http://127.0.0.1:" + str(node)
        )
    
    response = {
        'message': "Added new nodes",
        'total_nodes': list(blockchain.nodes)
    }

    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': "replaced",
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': "no change"
        }
    
    return jsonify(response), 200


if __name__ == "__main__":
    from argparse import ArgumentParser
    print(node_identifier)
    parser = ArgumentParser()

    parser.add_argument('-p', '--port',
                        default=5000,
                        type=int,
                        help="port num")
    
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port, 
            debug=True)