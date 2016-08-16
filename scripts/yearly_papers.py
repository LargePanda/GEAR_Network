import json
# local import 
from data_collection_util import *

import os
pr_path = os.path.join('..', 'profile', 'profile.json')

import codecs

# load original profile
with open(pr_path) as f:
    orig_profile = json.load(f)

paper_set = download_full_paper_set(orig_profile)


def papers_by_year(paper_set, year):

    paper_set_year = {}
    count = 0
    
    for mathsci_id in paper_set.keys():
        for paper in paper_set[mathsci_id]:
            if paper['date'] == year:
                count += 1
                paper_set_year[paper['id']] = paper

    print "Completed!", count, "papers are published in", str(year)
    return paper_set_year

def export_papers(paper_set, year):
	output_path = os.path.join('..', 'papers_by_year', str(year) + '.json')
	with codecs.open(output_path, "w", 'utf-8') as f: 
		json.dump(paper_set, f, indent=4, separators=(',', ': '), ensure_ascii = False)


for year in range(2009, 2017):
	print "Exporting year of", str(year)
	paper_set_year = papers_by_year(paper_set, year)
	export_papers(paper_set_year, year)