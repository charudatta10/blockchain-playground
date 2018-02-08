"""
block format we are going to use

block {
    'index': 1,
    'timestamp': 15060....,
    'transactions': [
        {
            'sender': 'sender_code',
            'recipient': 'recipient_code',
            'amount': 5
        }
    ],
    'proof': 32498474000,
    'previous_hash': '2cf2c...'
}


"""

import hashlib
import json
import random
import requests
from urlparse import urlparse
from time import time



class Blockchain(object):
    # Blockchain class

    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        # create the genesis block
        self.new_block(previous_hash=1, proof=100)


    def new_block(self, proof, previous_hash=None):
        """
        Create a new block and adds it to the chain

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (optional) <str> Hash of previous block
        :return: <dict> new block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }
        self.current_transactions = []
        self.chain.append(block)
        return block


    def new_transaction(self, sender, recipient, amount):
        """
        Create a new transaction

        :param sender: <str> Address of the sender
        :param recipient: <str> Address of the recipient
        :param amount: <int> Amount
        :return: <int> Index of the block where the transaction is added
        """
        
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        
        return self.last_block['index'] + 1


    @property
    def last_block(self):
        # returns the last block in the chain
        return self.chain[-1]


    @staticmethod
    def hash(block):
        # creates a SHA-256 hash of a block
        
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    
    def proof_of_work(self, last_proof):
        """
        Simple Proof of Work Algorithm:
            - Find a number p' such that hash(pp') contains 4 leading zeroes, 
              where p is the previous proof
            - p' is the new proof
        
        :param last_proof: <int>
        :return: <int>
        """

        proof = random.randint(0, 1000000)
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        
        return proof


    @staticmethod
    def valid_proof(last_proof, proof):
        # Validates the Proof
        guess = (str(last_proof) + str(proof)).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"



    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)



    def valid_chain(self, chain):
        # Determine if a given chain is valid
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            if block['previous_hash'] != self.hash(last_block):
                return False
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False
            last_block = block
            current_index += 1
        
        return True

    
    def resolve_conflicts(self):
        neighbors = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbors:
            response = requests.get('http://%s/chain'%node)
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # compire length
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False

    


