from flask import Flask, jsonify, render_template, request
from flask_cors import CORS, cross_origin
import numpy as np
import pickle
import json
# from sklearn.feature_extraction.text import TfidfVectorizer

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

MODEL = 'C'
simMatrixPath = {
    'A': 'similarity_matrix.npy',
    'B': 'similarity_matrix_model_b.npy',
    'C': 'similarity_matrix_model_c.npy',
}

# def load_model():
#     with open('tfidfmodel.pkl', 'rb') as f:
#         model = pickle.load(f)
#         return model
    
def load_artists():
    with open('filtered-indices.json', 'r') as f:
        artistToIndex = json.load(f)
        return artistToIndex

def load_sim_matrix():
    filePath = simMatrixPath[MODEL]
    return np.load(filePath)
    
simMatrix = load_sim_matrix()
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

@app.route('/recommend', methods=['GET'])
@cross_origin()
def get_recommendations():
    artistIndex = int(request.args.get('id'))
    artistSimVector = simMatrix[artistIndex]
    simVectorWithNames = [(indexToArtist[i], artistSimVector[i]) for i in range(len(artistSimVector))]
    sorted_similarities = sorted(simVectorWithNames, key=lambda x: x[1], reverse=True)
    return jsonify([{"name": x[0], "similarity": str(x[1])} for x in sorted_similarities[:5]])

@app.route('/artists/', methods=['GET'])
@app.route('/artists/<int:id>')
@cross_origin()
def get_artists(id=None):
    if id is not None:
        artistIndex = int(id) # TODO: better handling for bad input
        return jsonify({'name': indexToArtist[artistIndex], 'id': artistIndex})
    return jsonify([{"id": index, "name": name} for (name, index) in enumerate(artistToIndex)])

@app.route('/items', methods=['GET'])
@cross_origin()
def get_items():
    return jsonify(items)

if __name__ == '__main__':
    app.run(debug=True)