import json
# local import 
from data_collection_util import *

import os
pr_path = os.path.join('..', 'profile', 'profile.json')


# load original profile
with open(pr_path) as f:
    orig_profile = json.load(f)

# mappers for id and mathscinet id
mappers = make_mappers(orig_profile)
gear_mathsci_mapper = mappers[0]
mathsci_gear_mapper = mappers[1]

# download paper list for each member with mathsci_id

paper_set = download_full_paper_set(orig_profile)

paper_2011_meta = filter_2011(paper_set)

paper_set_2011 = paper_2011_meta[0]
count_2011 = paper_2011_meta[1]


# download papers citing gear member papers
download_gear_papers(paper_set_2011, count_2011)

# update coauthorship/cocitation data
full_paper_list = []
useful_paper = set()

# read arxiv
arxiv_path = os.path.join('..', 'arxiv', 'arxiv_papers.json')
arxiv_papers = read_arxiv(arxiv_path)

for ending_year in range(2011, 2017):
    update_collaborators(orig_profile, paper_set_2011, 2011, ending_year, mathsci_gear_mapper, useful_paper)
    update_citations(orig_profile, paper_set_2011, 2011, ending_year, mathsci_gear_mapper, full_paper_list, set())
    update_arxiv(orig_profile, arxiv_papers, 2011, ending_year)

# print matrix 
for ending_year in range(2011, 2017):
    matrix_maker(orig_profile, 2011, ending_year)


export_paper(full_paper_list, useful_paper)
export_profile(orig_profile)