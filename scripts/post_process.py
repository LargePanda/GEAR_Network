import os
import json
import codecs

def export(input_path, output_path, profile):
    for file_name in os.listdir(input_path):
        if file_name.endswith(".json"):
            output_website_input(file_name, input_path, output_path, profile)

def output_website_input(file_name, input_path, output_path, profile):
    
    input_file_path = os.path.join(input_path, file_name)
    output_file_path = os.path.join(output_path, file_name)

    print "Exporting" , input_file_path, "to", output_file_path

    with open(input_file_path, "r") as f:
        year_file = json.load(f)
    
    translator = {}
    for node in year_file['nodes']:
        id = node['id']  
        translator[id] = node['label']
    
    # trans is from graph id to member_id
    mg = {}
    for key in translator:
        mg[translator[key]] = key
     
    edge_weight = {}
    for edge in year_file['edges']:
        src = translator[edge['source']]
        tgt = translator[edge['target']]
        wt = edge['size']
        
        if src in edge_weight:
            edge_weight[src][tgt] = wt
        else:
            edge_weight[src] = {}
            edge_weight[src][tgt] = wt
        
        if tgt in edge_weight:
            edge_weight[tgt][src] = wt
        else:
            edge_weight[tgt] = {}
            edge_weight[tgt][src] = wt
    
            
    for node in year_file['nodes']:
        id = translator[node['id']]
        person = get_person(id, profile)
        
        person["size"] = node['size']
        person["pos_x"] = (node['x']+5000)/10000*800
        person["pos_y"] = (node['y']+5000)/10000*600
        person["cluster_id"] = int(node['attributes']['Modularity Class'])
        try:
            person["edges"] = edge_weight[id]
        except:
            person[id]["edges"] = {}
    
    with codecs.open(output_file_path, "wb", 'utf-8') as f:
        json.dump(profile, f, indent=4, separators=(',', ': '), ensure_ascii=False)


def get_person(target_id, profile):
    for person in profile['items']:
        person_id = str(person['member_id'])
        if target_id == person_id:
            return person

if __name__ == "__main__":

    co_citation_input_path = os.path.join( '..', 'gephi_output', 'co-citation') 
    co_authorship_input_path = os.path.join( '..', 'gephi_output', 'co-authorship') 

    co_citation_output_path = os.path.join( '..', 'website_input', 'co-citation') 
    co_authorship_output_path = os.path.join( '..', 'website_input', 'co-authorship') 

    profile_path = os.path.join( '..', 'website_input', 'profile.json') 
    

    with open(profile_path) as f:
        input_profile = json.load(f)
    
    export(co_authorship_input_path, co_authorship_output_path, input_profile)
    export(co_citation_input_path, co_citation_output_path, input_profile)
