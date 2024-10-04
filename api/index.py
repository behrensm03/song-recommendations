from flask import Flask, jsonify, render_template, request
import numpy as np
import pickle
import json
# from sklearn.feature_extraction.text import TfidfVectorizer

app = Flask(__name__)

def load_model():
    with open('tfidfmodel.pkl', 'rb') as f:
        model = pickle.load(f)
        return model
    
def load_artists():
    with open('filtered-indices.json', 'r') as f:
        artistToIndex = json.load(f)
        return artistToIndex
    
simMatrix = np.load("similarity_matrix.npy")
artistToIndex = load_artists()
indexToArtist = {artistToIndex[artist]: artist for artist in artistToIndex}

# sample data
items = [
  {'id': 1, 'name': 'item 1'},
  {'id': 2, 'name': 'item 2'}
]

# first thing we should do is set up a dropdown that shows all the artist names
# then when user selects one, use the similarity matrix to find the top 5 similar artists
# then render a list of those artists

artists = [a for a in artistToIndex]
@app.route('/')
def home():
    return render_template('index.html', options=artists)

@app.route('/submit', methods=['POST'])
def submit():
    selected_option = request.form.get('options')
    artistIndex = artistToIndex[selected_option]
    artistSimVector = simMatrix[artistIndex]
    simVectorWithNames = [(indexToArtist[i], artistSimVector[i]) for i in range(len(artistSimVector))]
    sorted_similarities = sorted(simVectorWithNames, key=lambda x: x[1], reverse=True)
    return render_template('submit.html', selection=selected_option, matches=sorted_similarities[:5])

@app.route('/items', methods=['GET'])
def get_items():
    return jsonify(items)

if __name__ == '__main__':
    app.run(debug=True)