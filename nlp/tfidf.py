import json
import io
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# If running in google colab, use this instead
# from google.colab import drive
# drive.mount('/content/drive', force_remount=True)
# root_path = os.path.join(os.getcwd(), "drive", "My Drive/grad cs/project/") # replace based on your Google drive organization

def loadArtistSummaries():
  nameToSummary = {}
  with io.open('../data/filtered-summaries.json') as f:
    nameToSummary = json.load(f)
  nameSummaryPairs = []
  for artist, summary in nameToSummary.items():
    nameSummaryPairs.append((artist, summary))
  return nameSummaryPairs

def saveTfIdfModel(nameSummaryPairs):
  vectorizer = TfidfVectorizer()
  nonEmptySummaries, nonEmptyNames = [], []
  for p in nameSummaryPairs:
    if p[1] != '':
      nonEmptySummaries.append(p[1])
      nonEmptyNames.append(p[0])
  fitCorpus = vectorizer.fit_transform(nonEmptySummaries)
  simMatrix = cosine_similarity(fitCorpus)
  np.save('similarity_matrix.npy', simMatrix)
