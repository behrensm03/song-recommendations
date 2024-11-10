from flask import Flask, jsonify, render_template, request, abort
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

MAX_INPUTS = 3

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

artists = [a for a in artistToIndex]
@app.route('/')
def home():
    return render_template('index.html', options=artists)

def getAverageMatchesForIndices(indices):
    simVectors = [simMatrix[index] for index in indices] # list of similarity vectors, for each input index
    aggSimWithNames = [(indexToArtist[i], sum([simVector[i] for simVector in simVectors]) / len(simVectors)) for i in range(len(simVectors[0]))] # for each match, get the average score across each simVector
    sortedAggSims = sorted(aggSimWithNames, key=lambda x: x[1], reverse=True)
    sortedFilteredAggSims = [x for x in sortedAggSims if artistToIndex[x[0]] not in indices]
    return jsonify([{"name": x[0], "similarity": str(x[1]), "id": artistToIndex[x[0]]} for x in sortedFilteredAggSims])

@app.route('/recommend', methods=['GET'])
@cross_origin()
def get_recommendations():
    artistIds = [int(x) for x in request.args.get('ids').split(',')]
    if len(artistIds) > MAX_INPUTS:
        abort(400)
    return getAverageMatchesForIndices(artistIds)

@app.route('/artists/', methods=['GET'])
@app.route('/artists/<int:id>')
@cross_origin()
def get_artists(id=None):
    if id is not None:
        artistIndex = int(id) # TODO: better handling for bad input
        return jsonify({'name': indexToArtist[artistIndex], 'id': artistIndex})
    return jsonify([{"id": index, "name": name} for (index, name) in enumerate(artistToIndex)])

if __name__ == '__main__':
    app.run(debug=True)