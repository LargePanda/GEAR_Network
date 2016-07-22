import scrapy
import requests
import urllib2
import BeautifulSoup
import pickle
import pyprind
import json
import collections
import matplotlib.pyplot as plt

# local import 
import mathscinet

import sys
sys.setdefaultencoding('utf-8')

with open("./profile/profile.json") as f:
    orig_profile = json.load(f)

# mappers for id and mathscinet id
gear_mathsci_mapper = {}
mathsci_gear_mapper = {}

for person in orig_profile['items']:
    gear_mathsci_mapper[person['member_id']] = person['mathsci_id']
    mathsci_gear_mapper[person['mathsci_id']] = person['member_id']


bar = pyprind.ProgBar(len(orig_profile['items']), bar_char='█', width=70)

paper_set = {}
for person in orig_profile['items']:    
    bar.update()
    member_id = person['member_id']
    mathsci_id = person['mathsci_id']
    if mathsci_id != 'NA':
        paper_set[mathsci_id] = mathscinet.find_papers(mathsci_id)

def transform_authors(paper, mathsci_gear_mapper):
	authors = paper['authors']
	paper['gear_authors'] = []
	for au in authors:
		mathsci_id = 'MR' + au
 		if mathsci_id in mathsci_gear_mapper:
 			paper['gear_authors'].append( mathsci_gear_mapper[mathsci_id] )


paper_set_2011 = {}
count_2011 = 0

for mathsci_id in paper_set.keys():    
    paper_set_2011[mathsci_id] = []
    for paper in paper_set[mathsci_id]:
        if paper['year'] >= 2011:
            count_2011 += 1
            transform_authors(paper, mathsci_gear_mapper)
            paper_set_2011[mathsci_id].append(paper)

print "Completed! count:", count_2011




bar = pyprind.ProgBar(count_2011, bar_char='█', width=70)
for mathsci_id in paper_set_2011.keys():
    for paper in paper_set_2011[mathsci_id]:
        bar.update()
        paper['citing'] = mathscinet.find_parent_citations(paper['article_id'])


def update_collaborators(cprofile, cpaper_set, starting_year, ending_year, converter):
    col_key = "%s-%s collaborators stats" % (str(starting_year), str(ending_year))

    for person in cprofile['items']:        
        collab_list = []
        mathsci_id = person['mathsci_id']
        if mathsci_id == "NA":
            continue
        for paper in cpaper_set[mathsci_id]:
            year = paper['year']
            if year < starting_year or year > ending_year:
                continue
            authors = ["MR"+au for au in paper['authors']]
            for au in authors:
                if au in converter:
                    collab_list.append(converter[au])
                    
        person[col_key] = dict(collections.Counter(collab_list))
        
    print "Done"