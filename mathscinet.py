import scrapy
import requests
import urllib2
import BeautifulSoup
import pickle
import pyprind


def get_article_year(div):
    full_text = get_text(div)
    for year in range(2000, 2017):
        if str(year) in get_desc(div):
            return year
    return -1

def get_article_date(div):
    return get_desc(div)

def get_article_id(div):
    num_tag = div.find('a', attrs = {"class":"mrnum"})
    return num_tag.text

def get_article_url(div):
    prefix = 'http://www.ams.org/mathscinet/search/publdoc.html?pg1=MR&s1='
    article_id = get_article_id(div)
    return prefix + article_id

def get_article_desc(div):
    return get_desc(div)

def get_article_authors(div):
    authors = []
    for author_link in div.findAll('a'):
        href = author_link.get("href")
        if "author" in href:
            authors.append("MR" + href[40:])
    return authors

def find_papers_by_author_id(mid):
    if "MR" in mid:
        mid = mid[2:]
        
    prefix = "http://www.ams.org/mathscinet/search/publications.html?pg1=INDI&s1="
    suffix = "&vfpref=html&r=1&extend=1"
    url = prefix + mid + suffix
    
    page = urllib2.urlopen(url).read()
    soup = BeautifulSoup.BeautifulSoup(page)
    divList = soup.findAll('div', attrs={ "class" : "headlineText"})
    
    info_list = []
    
    for div in divList:
        info = {}
        info['id'] = get_article_id(div)
        info['url'] = get_article_url(div)
        info['authors'] = get_article_authors(div)
        info['description'] = get_article_desc(div)
        info['date'] = get_article_year(div)
        info_list.append(info)

    return info_list

# sample:   
# http://www.ams.org/mathscinet/search/publdoc.html?pg1=MR&s1=2198773
def find_parent_citations(mid):
    if "MR" in mid:
        mid = mid[2:]

    prefix = "http://www.ams.org/mathscinet/search/publications.html?amp=&loc=refcit&refcit="
    suffix = "&vfpref=html&r=1&extend=1"
    
    url = prefix + mid + suffix
    
    page = urllib2.urlopen(url).read()
    soup = BeautifulSoup.BeautifulSoup(page)
    divList = soup.findAll('div', attrs={ "class" : "headlineText"})
    
    info_list = []
    
    for div in divList:
        info = {}
        info['id'] = get_article_id(div)
        info['url'] = get_article_url(div)
        info['authors'] = get_article_authors(div)
        info['description'] = get_article_desc(div)
        info['date'] = get_article_year(div)
        info_list.append(info)

    return info_list


# sample:
# http://www.ams.org/mathscinet/search/publications.html?amp=&loc=refcit&refcit=1085139&vfpref=html&r=1&extend=1
def find_children_citations(mid):
    
    prefix = "http://www.ams.org/mathscinet/search/publdoc.html?pg1=MR&s1="
    suffix = ""

    remid = mid[2:]
    url = prefix + remid + suffix
    
    page = urllib2.urlopen(url).read()
    soup = BeautifulSoup.BeautifulSoup(page)
    
    res = []
    
    link_list = soup.findAll('a')
    
    for link in link_list:
        text = link.text
        if len(text) > 3 and text[0:2] == 'MR':
            paper_id = text.strip()
            if paper_id != mid:
                res.append(paper_id)
                
    return res
    

def get_status(div):
    article_status_tag = div.find('a', attrs = {"class":"item_status"})
    try:
        return article_status_tag.text
    except:
        return ""

def get_text(div):
    spaced_text = " ".join(item.strip() for item in div.findAll(text=True))
    return spaced_text

def clean_text(title_text):
    no_newline_text = title_text.replace("\n", "")
    reduced_spaced_text = " ".join(no_newline_text.split())
    return reduced_spaced_text

def get_desc(div):
    full_text = get_text(div)
    article_status = get_status(div)
    
    index = full_text.find(article_status)
    start_index = index + len(article_status)
    end_index = full_text.find('SFXButton')
    
    return clean_text(full_text[start_index: end_index])


