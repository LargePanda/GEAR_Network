import requests
from bs4 import BeautifulSoup
import pyprind
import json
import collections
import os
import codecs

import mathscinet

def make_mappers(profile):
    """
    return mappers for id and mathscinet id
    """

    gear_mathsci_mapper = {}
    mathsci_gear_mapper = {}

    for person in profile['items']:
        gear_mathsci_mapper[person['member_id']] = person['mathsci_id']
        mathsci_gear_mapper[person['mathsci_id']] = person['member_id']

    return (gear_mathsci_mapper, mathsci_gear_mapper)


def download_full_paper_set(profile):
    bar = pyprind.ProgBar(len(profile['items']), width=70)

    paper_set = {}
    for person in profile['items']:    
        bar.update()
        member_id = person['member_id']
        mathsci_id = person['mathsci_id']
        if mathsci_id != 'NA':
            paper_set[mathsci_id] = mathscinet.find_papers_by_author_id(mathsci_id)

    return paper_set

def filter_2011(paper_set):

    paper_set_2011 = {}
    count_2011 = 0
    
    for mathsci_id in paper_set.keys():
        paper_set_2011[mathsci_id] = []
        for paper in paper_set[mathsci_id]:
            if paper['date'] >= 2011:
                count_2011 += 1
                paper_set_2011[mathsci_id].append(paper)

    print "Completed!", count_2011, "papers are published after 2011 (including 2011). "
    return (paper_set_2011, count_2011)

def download_gear_papers(paper_set, paper_count):
    # download papers citing gear member papers
    bar = pyprind.ProgBar(paper_count, width=70)

    for mathsci_id in paper_set.keys():
        for paper in paper_set[mathsci_id]:
            bar.update()
            paper['citing'] = mathscinet.find_parent_citations( paper['id'] )

def read_arxiv(filepath):
    with open(filepath) as f:
        arxiv_papers = json.load(f)
    return arxiv_papers

def update_arxiv(gear_profile, arxiv_papers, starting_year, ending_year):
    col_detail_key = "%s-%s collaborators details" % (str(starting_year), str(ending_year))
    col_size_key = "%s-%s collaborators sizes" % (str(starting_year), str(ending_year))

    for paper in arxiv_papers:
        year = paper['date']
        if year < starting_year or year > ending_year:
                continue
        ids = paper['authors']
        for member_id in ids:
            person = get_person_by_id(gear_profile, member_id)
            details = person[col_detail_key]
            
            for mid in ids:
                if mid != member_id:
                    # update detail
                    
                    if mid in details:
                        details[mid].append( paper['id'] )
                    else:
                        details[mid] = [ paper['id'] ]
                    
                    for key in details.keys():
                        person[col_size_key][key] = len(details[key])


def update_collaborators(gear_profile, gear_paper_set, starting_year, ending_year, converter, paper_collector):
    
    col_detail_key = "%s-%s collaborators details" % (str(starting_year), str(ending_year))
    col_size_key = "%s-%s collaborators sizes" % (str(starting_year), str(ending_year))
    
    for person in gear_profile['items']:
        details = {}
        sizes = {}
        
        mathsci_id = person['mathsci_id']

        # if mathsci_id does not exist, continue
        if mathsci_id == "NA":
            continue

        for paper in gear_paper_set[mathsci_id]:
            year = paper['date']

            if year < starting_year or year > ending_year:
                continue

            authors = paper['authors']

            for au in authors:
                if au in converter:
                    gear_id = converter[au]
                    
                    if gear_id == person['member_id']:
                        continue

                    paper_collector.add( paper['id'] )
                    
                    if gear_id in details:
                        details[gear_id].append( paper['id'] )
                    else:
                        details[gear_id] = [ paper['id'] ]
        
        for key in details.keys():
            sizes[key] = len(details[key])
            
        person[col_detail_key] = details
        person[col_size_key] = sizes

def get_citation_keys(citations):
    keys = []
    for cite in citations:
        keys.append(cite['id'])
    return keys

def retrieve_citations(person, selected_paper_set, starting_year, ending_year, the_paper_list):
    
    mathsci_id = person['mathsci_id']
    
    citations = []
    
    if mathsci_id == "NA":
        return citations
    
    paper_list = selected_paper_set[mathsci_id]
    the_paper_list.extend(paper_list)

    for paper in paper_list:
        year = paper['date']
        if year < starting_year or year > ending_year:
            continue
        the_paper_list.extend(paper['citing'])
        citations.extend( get_citation_keys(paper['citing']) )
     
    return citations

def list_overlap(list_a, list_b):

    a_multiset = collections.Counter(list_a)
    b_multiset = collections.Counter(list_b)

    overlap = list((a_multiset & b_multiset).elements())
    
    return overlap

def update_citations(profile, paper_set, starting_year, ending_year, converter, the_paper_list, paper_collector):
    
    cite_details_key = "%s-%s citation details" % (str(starting_year), str(ending_year))
    cite_sizes_key = "%s-%s citation sizes" % (str(starting_year), str(ending_year))
    
    # build member_id -> person mapping
    temp_profile = {}
    for person in profile['items']:
        member_id = person['member_id']
        temp_profile[member_id] = person

    author_list = temp_profile.keys()

    for person in profile['items']:
        person[cite_details_key] = {}
        person[cite_sizes_key] = {}
        
        member_id = person['member_id']
        
        for other_person_id in author_list:
            
            if other_person_id == member_id:
                continue
            
            other_person = temp_profile[other_person_id]
            
            other_person_citation = retrieve_citations(other_person, paper_set, starting_year, ending_year, the_paper_list)
            this_person_citation = retrieve_citations(person, paper_set, starting_year, ending_year, the_paper_list)
            
            for pid in list_overlap(other_person_citation, this_person_citation):
                paper_collector.add(pid)

            length = len(list_overlap(other_person_citation, this_person_citation)) 
            if length > 0:
                person[cite_details_key][other_person_id] = list_overlap(other_person_citation, this_person_citation)
                person[cite_sizes_key][other_person_id] = len(person[cite_details_key][other_person_id])


def print_matrix(folder_name, file_name, matrix):
    path = os.path.join('..', folder_name, file_name)
    print path
    with open(path, "w") as f:
        f.write("Source;Target;Weight;Type\n")
        for key in matrix.keys():
            f.write(str(key[0]) + ";")
            f.write(str(key[1]) + ";")
            f.write(str(matrix[key]) + ";")
            f.write("undirected\n")


def matrix_maker(gear_profile, starting_year, ending_year):
    collab_matrix = {}
    citation_matrix = {}
    
    cit_size_key = "%s-%s citation sizes" % (str(starting_year), str(ending_year))
    col_size_key = "%s-%s collaborators sizes" % (str(starting_year), str(ending_year))
    
    for person in gear_profile['items']:
        
        if person['mathsci_id'] == "NA":
            continue
        
        author_id = person['member_id']
        
        for key in person[col_size_key].keys():
            if key > author_id:
                collab_matrix[(author_id, key)] = person[col_size_key][key]
        
        for key in person[cit_size_key].keys():
            if key > author_id:
                citation_matrix[(author_id, key)] = person[cit_size_key][key]
                
    print_matrix("gephi_input", str(starting_year)+"_"+str(ending_year)+"_citation.csv", citation_matrix)
    print_matrix("gephi_input", str(starting_year)+"_"+str(ending_year)+"_coauthor.csv", collab_matrix)


def export_paper(the_paper_list, paper_collector, arxiv_papers): 
    print "Exporting papers ..."
    output_path = os.path.join( '..', 'website_input', 'papers.json') 
    export = {} 

    for p in the_paper_list: 
        p.pop('citing', None)
        if p['id'] in paper_collector:
            export[p['id']] = p 
    for p in arxiv_papers:
        export[p['id']] = p

    with codecs.open(output_path, "w", 'utf-8') as f: 
        json.dump(export, f, indent=4, separators=(',', ': '), ensure_ascii = False)

def export_profile(profile):
    print "Exporting profile ..."
    output_path = os.path.join( '..', 'website_input', 'profile.json') 
    with codecs.open(output_path, "w", 'utf-8') as f: 
        json.dump(profile, f, indent=4, separators=(',', ': '), ensure_ascii = False)

def get_person_by_id(profile, member_id):
    for person in profile['items']:
        if person['member_id'] == member_id:
            return person
