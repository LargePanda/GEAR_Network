import requests
import BeautifulSoup
import pyprind
import json
import collections
import os

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


def update_collaborators(gear_profile, gear_paper_set, starting_year, ending_year, converter):
    
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

def retrieve_citations(person, selected_paper_set, starting_year, ending_year):
    
    mathsci_id = person['mathsci_id']
    
    citations = []
    
    if mathsci_id == "NA":
        return citations
    
    paper_list = selected_paper_set[mathsci_id]
    
    for paper in paper_list:
        year = paper['date']
        if year < starting_year or year > ending_year:
            continue
        citations.extend( get_citation_keys(paper['citing']) )
        
    return citations

def list_overlap(list_a, list_b):

    a_multiset = collections.Counter(list_a)
    b_multiset = collections.Counter(list_b)

    overlap = list((a_multiset & b_multiset).elements())
    
    return overlap

def update_citations(profile, paper_set, starting_year, ending_year, converter):
    
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
            
            other_person_citation = retrieve_citations(other_person, paper_set, starting_year, ending_year)
            this_person_citation = retrieve_citations(person, paper_set, starting_year, ending_year)
            
            length = len(list_overlap(other_person_citation, this_person_citation)) 
            if length > 0:
                person[cite_sizes_key][other_person_id] = list_overlap(other_person_citation, this_person_citation)
                person[cite_sizes_key][other_person_id] = len(person[cite_sizes_key][other_person_id])


def print_matrix(folder_name, file_name, matrix):
    path = os.path.join(folder_name, file_name)
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
                
    print_matrix("output", str(starting_year)+"_"+str(ending_year)+"_citation", citation_matrix)
    print_matrix("output", str(starting_year)+"_"+str(ending_year)+"_coauthor", collab_matrix)