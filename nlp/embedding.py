import spacy
import io
import json
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
nlp = spacy.load("en_core_web_lg")

# from google.colab import drive
# import os
# drive.mount('/content/drive', force_remount=True)

def loadArtistToSummary():
  with io.open("filtered-summaries.json") as f:
    artistToSummary = json.load(f)
  return artistToSummary

def getEmbeddingMatrix(artistToSummary):
  pairs = [(artist, summary) for artist, summary in artistToSummary.items()]
  embeddingMatrix = []
  for i in range(len(pairs)):
    doc = nlp(pairs[i][1])
    embeddingMatrix.append(doc.vector)

def saveEmbeddingModel(embeddingMatrix):
  similarityMatrix = cosine_similarity(embeddingMatrix)
  np.save('similarity_matrix_embedding_model.npy', similarityMatrix)