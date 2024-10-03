from flask import Flask, jsonify

app = Flask(__name__)

# sample data
items = [
  {'id': 1, 'name': 'item 1'},
  {'id': 2, 'name': 'item 2'}
]

@app.route('/')
def home():
    return 'new Hello, World!'

@app.route('/about')
def about():
    return 'About'

@app.route('/items', methods=['GET'])
def get_items():
    return jsonify(items)