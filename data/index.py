# Note: this requires python >= 3.8 to run (wikipedia-api requires it).
# My mac is too old to run that, so this has some code for running in a google colab notebook
# or something similar which can access that python version

# import wikipediaapi
import requests
from concurrent.futures import ThreadPoolExecutor
import os
import io
import json

root_path = os.path.join(os.getcwd(), "data")
# If running in google colab, use this instead
# from google.colab import drive
# drive.mount('/content/drive', force_remount=True)
# root_path = os.path.join(os.getcwd(), "drive", "My Drive/grad cs/project/") # replace based on your Google drive organization

class WikipediaSearcher:
  def __init__(self):
    self.wiki = wikipediaapi.Wikipedia('Wikipedia Searcher', 'en')
    self.session = requests.Session()

  # this requires title to be exact
  def summary(self, title):
    page = self.wiki.page(title)
    return page.summary

  def search(self, query):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query
    }
    resp = self.session.get(url=url, params=params)
    data = resp.json()
    return [data['query']['search'][i]['title'] for i in range(len(data['query']['search']))]

  def guess(self, query):
    titles = self.search(query)
    if len(titles) == 0:
      return "", False
    return self.summary(titles[0]), True

class WikipediaParallelSearcher:
  def __init__(self, max_threads=10, verbose=False):
    self.wiki = WikipediaSearcher()
    self.max_threads = max_threads
    self.executor = ThreadPoolExecutor(max_workers=max_threads)
    self.verbose = verbose

  def search(self, query):
    summary, ok = self.wiki.guess(query)
    return summary if ok else ""

  async def fetch_all(self, queries):
    if self.verbose:
      print("Fetching", len(queries), "queries")
    results = list(self.executor.map(self.search, queries))
    return results

def loadArtistNames():
  with io.open(os.path.join(root_path, "artists_names_only.csv"), encoding='utf8') as f:
    artist_names_file = f.read()
    return artist_names_file.split("\n")

async def fetchSummaries(artist_names):
  wikiFetcher = WikipediaParallelSearcher(10)
  artist_summaries = await wikiFetcher.fetch_all(artist_names)
  return artist_summaries
  
async def fetchAndSaveArtistSummaries():
  artist_names = loadArtistNames()
  summaries = await fetchSummaries(artist_names)
  artistToSummary = {artist_names[i]: summaries[i] for i in range(len(summaries))}
  with io.open(os.path.join(root_path, "name-to-summary-raw.json"), 'w') as f:
    json.dump(artistToSummary, f)

def getAmbiguousSummaries(artistSummaryLookup):
  ambiguous, missing = [], []
  # words we think at least one of is likely to appear in any musician bio
  keywords = ["music", "singer", "songwriter", "rapper", "band"] 
  for artist in artistSummaryLookup.keys():
    # search terms that don't yield a wiki page typically have "will refer to" in the search results page
    if "may refer to:" in artistSummaryLookup[artist] or "may also refer to:" in artistSummaryLookup[artist]:
      ambiguous.append(artist)
    elif artistSummaryLookup[artist] == "":
      missing.append(artist)
    else:
      for keyword in keywords:
        if keyword in artistSummaryLookup[artist]:
          break
      else:
        ambiguous.append(artist)
  return ambiguous, missing

async def loadDisambiguatedLinks(wikiFetcher):
  disambiguationPartial = {}
  with io.open(os.path.join(root_path, "disambiguation_partial.json")) as f:
    disambiguationPartial = json.load(f)
  disambiguated = []
  for ambig in disambiguationPartial:
    correct = disambiguationPartial[ambig]
    if correct != '':
      disambiguated.append(correct)
  disambiguatedSummaries = await wikiFetcher.fetch_all(disambiguated)
  return disambiguatedSummaries

def saveDisambiguatedSummaries(disambiguatedLinks, disambiguatedSummaries, disambiguationPartial):
  nameToDisambiguated = {}
  temp = {}
  for i in range(len(disambiguatedLinks)):
    temp[disambiguatedLinks[i]] = disambiguatedSummaries[i]
  for name in disambiguationPartial:
    if disambiguationPartial[name] != '':
      nameToDisambiguated[name] = temp[disambiguationPartial[name]]
  with io.open(os.path.join(root_path, "disambiguated-summaries.json"), 'w') as f:
    json.dump(nameToDisambiguated, f)

def saveNameToSummary(artistSummaryLookup, ambiguousLookup, nameToDisambiguated):
  nameToSummary = {}
  for artist, preloaded_summary in artistSummaryLookup.items():
    if artist in ambiguousLookup.keys():
      nameToSummary[artist] = ''
    else:
      nameToSummary[artist] = preloaded_summary
  for artist, summary in nameToDisambiguated.items():
    nameToSummary[artist] = summary
  with io.open(os.path.join(root_path, "name-to-summary.json"), 'w') as f:
    json.dump(nameToSummary, f)