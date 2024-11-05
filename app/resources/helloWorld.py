from flask import Blueprint, jsonify

hello_world = Blueprint('hello_world', __name__)

@hello_world.route('/hello', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello, World!'}), 200