
import json
import sys
from data_collection_util import *

pr_path = os.path.join('..', 'profile', 'profile.json')
# load original profile
with open(pr_path) as f:
    orig_profile = json.load(f)

mappers = make_mappers(orig_profile)
gear_mathsci_mapper = mappers[0]
mathsci_gear_mapper = mappers[1]


papers_path = os.path.join('..', 'website_input', 'papers.json')
output_path = os.path.join('..', 'website_input', 'new_papers.json')

with codecs.open(papers_path, "r", 'utf-8') as f: 
	papers = json.load(f)

for pid in papers.keys():
	if "MR" not in pid:
		continue
	p = papers[pid]
	pre_authors = p['authors']
	p['authors'] = []
	for author in pre_authors:
		if author in mathsci_gear_mapper:
			p['authors'].append(mathsci_gear_mapper[author])

with codecs.open(output_path, "w", 'utf-8') as f: 
	json.dump(papers, f, indent=4, separators=(',', ': '), ensure_ascii = False)
