import hashlib
import json
from time import time
from uuid import uuid4
from flask import Flask, request, jsonify
from textwrap import dedent
# import jasonify


class learn_blockchaining(object):
  def __init__(self):
    self.chain = []

    self.current_transaction = []


    # creating a genisis block
    self.new_block(previous_hash = 1 , proof = 100)

  def new_block(self, proof, previous_hash = None):
    '''
    creates a new block and add it to the chain
    : param proof : <int> gives the proof of work 
    : param previous_hash <str> hash the previous block
    : return : <dict> new block
    '''
    
    block = {
      'index' : len(self.chain) + 1 ,
      'timestamp' : time(),
      'transactions' : self.current_transaction,
      'proof' : proof,
      'previous_hash' : previous_hash or self.hash(self.chain[-1]),
    }

    # reset the current list of transactions
    self.current_transaction = []
    self.chain.append(block)

    return block

  def new_transaction(self, sender, recipient, amount):
    '''
    adds a new transaction to the list of the transanctions
    : sender : <str> address of the sender
    : receiver : <str> address of the  receiver
    : amount : <int> amount
    : return : <int> index that will hold the index of this transactions
    '''
    
    self.current_transaction.append({
      'sender' : sender,
      'recipient' : recipient,
      'amount' : amount,
    })

    return self.last_block['index'] + 1



  @staticmethod
  def hash(block):
    '''
    hashes the block of the transaction
    creates a sha-256 hash of a block
    : param block : <dict> block
    : return : <str>
    '''

    # we must make sure that the dictionary is ordered 

    block_string = json.dumps(block , sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

  @property
  def last_block(self):
    '''
    returns the last block in the chain
    '''
    return self.chain[-1]



  def proof_of_work(self, last_proof):
    '''
    A simple algorithm that will illustrates the PoW
    - find a number p' such that the hash of (pp') contains leading 4 zeros, where p is the previous of p'
    - p is the previous proof and the p' is the new proof
    : param last_proof : <int>
    : return : <int>
    '''

    proof = 0
    while self.valid_proof(last_proof,proof) is False:
      proof += 1

    return proof


  @staticmethod
  def valid_proof(last_proof, proof):
    '''
    validates the proof
    param last_proof : <int>, the previous proof
    param proof : <int> the current proof
    return : <bool> True if correct and false if not
    '''

    guess = f'{last_proof}{proof}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    
    return guess_hash[:4] == '0000'
    




# creating an instance of our app

app = Flask(__name__)

# generate a new globally unique address for this node
node_identifier = str(uuid4()).replace('_', '')

# instanciate the blockchain
blockchain = learn_blockchaining()

# a route with the get method
@app.route('/mine', methods=['GET'])
def mine():

  # we run the PoW algorithim
  last_block = blockchain.last_block
  last_proof = blockchain.last_block['proof']
  proof = blockchain.proof_of_work(last_proof)

  # we must receive an award for finding the proof
  # the sender is 0 to signify that this node has mined this coin
  blockchain.new_transaction(
    sender = '0',
    recipient = node_identifier,
    amount = 1,
  ) 
  
  # Forge the new block by adding it to the chain
  previous_hash = blockchain.hash(last_block)
  block = blockchain.new_block(proof, previous_hash)

  response = {
    'message' : 'New Block Forged',
    'index' : block['index'],
    'transactions' : block['transactions'],
    'proof' : block['proof'],
    'previous_hash' : block['previous_hash']
  }

  return jsonify(response), 200

# a route with a post method
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
  values = request.get_json()

  # check the validity of the data
  required = ['sender', 'recipient', 'amount']
  if not all(k in values for k in required):
    return 'Missing certain values', 400

  # create a new transaction
  index = blockchain.new_transaction(values['sender'],values['recipient'],values['amount'])

  response = {'message': f'Transaction will be added to Block {index}'}

  return jsonify(response), 201


@app.route('/chain',methods=['GET'])
def full_chain():
  response = {
    'chain' : blockchain.chain,
    'length' : len(blockchain.chain)
  }
  return jsonify(response), 200



if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)
