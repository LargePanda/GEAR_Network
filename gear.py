import scrapy
import requests
import urllib2
import BeautifulSoup
import pickle
import pyprind
import json
import collections
import matplotlib.pyplot as plt

# MathSciNet API
import mathscinet

# logging info at "app.log"
import logging


def main():
	logging.basicConfig(filename='app.log', level=logging.INFO)
	orig_profile = load_profile()
	paper_set = scrape_papers(prof)
	paper_set_2011 = select_papers(paper_set)

	
def hint(info_text):
	logging.info(info_text)
	print(info)

def load_profile():

	hint("Loading original profile")
	with open("original_profile.json") as f:
    	orig_profile = json.load(f)
    hint("Done Loading")
    
    return orig_profile

def scrape_papers(profile):
	
	hint("Start scraping papers")
	print("Estimated runnning time: 5 min")
	
	bar = pyprind.ProgBar(len(orig_profile['items']), bar_char='█', width=70)
	
	paper_set = {}
	for person in orig_profile['items']:
    	bar.update()
    	member_id = person['member_id']
    	mathsci_id = person['mathsci_id']
    
    	if mathsci_id != 'NA':
        	paper_set[mathsci_id] = mathscinet.find_papers(mathsci_id)
    
    hint("Done scraping papers")
    return paper_set
    
def select_papers(paper_set):
	paper_set_2011 = {}
	
	count_2011 = 0

	for mathsci_id in paper_set.keys():
    
    	paper_set_2011[mathsci_id] = []
    
    	for paper in paper_set[mathsci_id]:
        	if paper['year'] >= 2011:
            	count_2011 += 1
            	paper_set_2011[mathsci_id].append(paper)
            	
    hint("There are "+str(count_2011)+" papers after 2011")
    return paper_set_2011 = {}


def scraping_citations(paper_set_2011):
    hint("Start scraping citations")
	print("Estimated runnning time: 20 min")
	
	bar = pyprind.ProgBar(count_2011, bar_char='█', width=70)

	for mathsci_id in paper_set_2011.keys():
    
    	for paper in paper_set_2011[mathsci_id]:
        	bar.update()
        	paper['citing'] = mathscinet.find_children_citations(paper['article_id'])
    
    hint("Done scraping citations")

"""
===============
Profile Update
===============
"""
def profile_update(profile, paper_set_2011):
	converter = build_id_converter(profile)
	for ending_year in range(2011, 2016):
    	update_collaborators(orig_profile, paper_set_2011, 2011, ending_year, converter)
    	update_citations(orig_profile, paper_set_2011, 2011, ending_year, converter)
    hint("Done updating profile")

def build_id_converter():
	"""
	Build a mapping: mathscinet_id -> member_id
	"""
	id_converter = {}

	for person in orig_profile['items']:
    	id_converter[person['mathsci_id']] = person['member_id']
    return id_converter
    	
def update_collaborators(cprofile, cpaper_set, starting_year, ending_year, converter):
	"""
	Function to update profile (collaborators)
	"""
    col_key = "%s-%s collaborators stats" % (str(starting_year), str(ending_year))
    print col_key
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


def update_citations(cprofile, cpaper_set, starting_year, ending_year, converter):
    """
	Function to update profile (citations)
	"""
    cit_key = "%s-%s citation stats" % (str(starting_year), str(ending_year))
    print cit_key    
    
    # build member_id -> person mapping
    temp_profile = {}
    for person in cprofile['items']:
        member_id = person['member_id']
        temp_profile[member_id] = person
        
    au_list = temp_profile.keys()

    for person in cprofile['items']:
        person[cit_key] = {}
        
        member_id = person['member_id']
        
        for other_person_id in au_list:
            if other_person_id == member_id:
                continue
            other_person = temp_profile[other_person_id]
            
            other_person_citation = retrieve_citations(other_person, cpaper_set, starting_year, ending_year)
            this_person_citation = retrieve_citations(person, cpaper_set, starting_year, ending_year)

            weight = len(list_overlap(other_person_citation, this_person_citation))
            if weight != 0:
                person[cit_key][other_person_id] = weight
            
    print "Done"  	
   
    
def list_overlap(list_a, list_b):

    a_multiset = collections.Counter(list_a)
    b_multiset = collections.Counter(list_b)

    overlap = list((a_multiset & b_multiset).elements())
    
    return overlap
if __name__ == "__main__":
	main()
	