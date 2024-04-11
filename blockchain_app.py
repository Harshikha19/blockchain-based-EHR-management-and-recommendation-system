from hashlib import sha256
import json
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request
from flask import Flask, jsonify, request
from import_ipynb import NotebookLoader



class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create genesis block
        self.new_block(previous_hash='1', proof=100)

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, data):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'data': data,
        })
        return self.last_block['index'] + 1

    def hash(self, block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"  # Adjust difficulty by changing number of zeros

    def get_patient_data(self, patient_id):
        for block in reversed(self.chain):
            for tx in block['transactions']:
                if 'data' in tx and tx['data'].get('patient_id') == patient_id:
                    return tx['data']
        return None

    def generate_recommendations(self, patient_data):
        recommendations = []

        # Age-based recommendations
        age = patient_data.get('age')
        if age is not None:
            if age >= 50:
                recommendations.append("Consider regular screenings for age-related conditions")
            if age >= 65:
                recommendations.append("Discuss flu vaccination and pneumonia vaccine with healthcare provider")

        # Disease-specific recommendations
        medical_history = patient_data.get('medical_history', [])

        if 'Diabetes' in medical_history:
            recommendations.append("Monitor blood sugar levels regularly and follow dietary guidelines")

        if 'Hypertension' in medical_history:
            recommendations.append("Maintain a low-sodium diet and engage in regular physical activity")

        if 'Cancer' in medical_history:
            recommendations.append("Follow recommended cancer screenings and treatment plans")

        # If patient has multiple diseases, provide combined recommendations
        if 'Diabetes' in medical_history and 'Hypertension' in medical_history:
            recommendations.append("Manage both diabetes and hypertension simultaneously for optimal health")

        # Other personalized recommendations based on patient data
        # Add more recommendations based on specific patient attributes...

        return recommendations

# Instantiate the Node
app = Flask(__name__)

# Instantiate the Blockchain
blockchain = Blockchain()

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

@app.route('/mine', methods=['POST'])
def mine():
    # Extract data from the POST request
    data = request.get_json()

    # Validate required fields in the request data
    required_fields = ['sender', 'recipient', 'data']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400

    sender = data['sender']
    recipient = data['recipient']
    custom_data = data['data']

    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # We must receive a reward for finding the proof.
    blockchain.new_transaction(
        sender=sender,
        recipient=recipient,
        data=custom_data
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    # Extract patient_id from the POST request
    data = request.get_json()
    patient_id = data.get('patient_id')

    if not patient_id:
        return jsonify({'message': 'Patient ID is required'}), 400

    # Get patient data from the blockchain
    patient_data = blockchain.get_patient_data(patient_id)

    if not patient_data:
        return jsonify({'message': 'Patient data not found'}), 404

    # Generate recommendations based on patient data
    recommendations = blockchain.generate_recommendations(patient_data)

    response = {
        'patient_id': patient_id,
        'recommendations': recommendations
    }

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='localhost', port=5000)
