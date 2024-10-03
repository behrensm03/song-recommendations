from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'new Hello, World!'

@app.route('/about')
def about():
    return 'About'