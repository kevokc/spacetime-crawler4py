from curses.ascii import isalnum
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
import string

Uniques = set()
LongestPage = ""
LongestWordCount = 0
MCW = []
Subdomains = dict()

def scraper(url, resp):
    if (resp.status != 200) or (resp.raw_response.content == None):
        return list()

    links = extract_next_links(url, resp)

    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    global LongestPage
    global LongestWordCount
    global MCW

    if resp.status != 200:
        return list()
        
    soup = BeautifulSoup(resp.raw_response.content.decode('utf-8', 'ignore'), 'html.parser')

    #tokenize
    contents = soup.get_text()
    list1 = contents.split()
    for a in list1:
        if not a.isalnum():
            list1.remove(i)
    
    #counter = 0
    #DELETING = False
    #for a in contents:
        #if DELETING == False:
            #if a.isalnum() == False:
                #contents[counter] = " "
                #DELETING = True
        #else:
            #if a == " ":
                #DELETING = False
            #contents[counter] = " "
        #counter += 1
    
    #list1 = "".join(contents).split()
    
    if len(list1) > LongestWordCount:
        LongestWordCount = len(list1)
        LongestPage = url
    
    list2 = []
    for b in list1:
        if b.lower() not in stopwords.words('english'):
            list2.append(b.lower())

    if (len(list2) / len(list1)) <= 0.5:
        return list()

    unq = list(set(list2))
    my_dict = {}
    for d in unq:
        my_dict[d] = 0
    for e in list2:
        my_dict[e] += 1
    list3 = list(my_dict.items())
    MCW.extend(list3)
    #tokenize

    final_list = []
    for i in soup.find_all('a'):
        my_url = i.get('href')
        if my_url != None:
            final_list.append(my_url)

    return final_list

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    global Uniques

    try:
        parsed = urlparse(url)

        valids = [".ics.uci.edu",".cs.uci.edu",".informatics.uci.edu",".stat.uci.edu","today.uci.edu/department/information_computer_sciences"]
        
        if (parsed.hostname == None) or (parsed.netloc == None) or (parsed.scheme not in ["http", "https"]):
            return False

        hostname_check = False
        for i in valids:
            if i in parsed.hostname:
                hostname_check = True

        if hostname_check and \
            not re.search(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|z|php"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ppt|pptx|ppsx)$", parsed.path.lower()):
                pos = url.find('#')
                if pos != -1:
                    url_in_q = url[:pos]
                    if url_in_q not in Uniques:
                        Uniques.add(url_in_q)
                        
                return True    
        else:
            return False

    except TypeError:
        print ("TypeError for ", parsed)
        raise
