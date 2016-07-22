import scrapy
import requests
import urllib2
import BeautifulSoup
import pickle
import pyprind

# http://www.ams.org/mathscinet/search/publdoc.html?pg1=MR&s1=2198773

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
    

# sample_url 

# http://www.ams.org/mathscinet/search/publications.html?amp=&loc=refcit&refcit=1085139&vfpref=html&r=1&extend=1
def find_parent_citations(mid):
    prefix = "http://www.ams.org/mathscinet/search/publications.html?amp=&loc=refcit&refcit="
    suffix = "&vfpref=html&r=1&extend=1"
     
    remid = mid[2:]
    url = prefix + remid + suffix
    
    page = urllib2.urlopen(url).read()
    soup = BeautifulSoup.BeautifulSoup(page)
    divList = soup.findAll('div', attrs={ "class" : "headlineText"})
    info_list = []
    
    for div in divList:
        num = div.find('a', attrs = {"class":"mrnum"})
        article_id = num.text
        link = num.get("href")

        authors = []
        for author_link in div.findAll('a'):
            href = author_link.get("href")
            if "author" in href:
                authors.append(href[40:])

        article_title = extract_title(div.text)
        
        info = {}
        
        info['article_id'] = article_id
        info['article_link'] = link
        info['article_title'] = article_title
        info['year'] = extract_year(article_title)
        info['authors'] = authors
        
        info_list.append(info)

    return info_list
    

# sample url: http://www.ams.org/mathscinet/search/publications.html?pg1=INDI&s1=304864&vfpref=html&r=1&extend=1
def find_papers(mid):
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
        num = div.find('a', attrs = {"class":"mrnum"})
        article_id = num.text
        link = num.get("href")

        authors = []
        for author_link in div.findAll('a'):
            href = author_link.get("href")
            if "author" in href:
                authors.append(href[40:])

        article_title = extract_title(div.text)

        info = {}
        info['article_id'] = article_id
        info['article_link'] = link
        info['article_title'] = article_title
        info['authors'] = authors
        info['year'] = extract_year(article_title)        
        info_list.append(info)
        
    return info_list
    

def extract_year(text):
    for i in range(2011, 2017):
        if str(i) in text:
            return i
    return 0
    

def extract_title(text):
    pref = text[0:20]
    if "Pending" in pref:
        start = text.find('Pending')+7
    elif "Reviewed" in pref:
        start = text.find('Reviewed')+8
    elif "Indexed" in pref:
        start = text.find('Indexed')+7
    elif "Prelim" in pref:
        start = text.find('Indexed')+6
    elif "Thesis" in pref:
        start = text.find('Indexed')+6
    try:
        h = start
    except:
        print pref
        
    end = text.find('SFXButton(')
    return text[start:end].replace("\n", " ")
    
