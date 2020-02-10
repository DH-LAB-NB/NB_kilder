import dhlab.nbtext as nb
from dhlab.nbtokenizer import tokenize
from collections import Counter
import pandas as pd

import zipfile
from bs4 import BeautifulSoup
import sys
import zipfile
import re
from IPython.display import display, Markdown

## Korpuset kommer som en zip

def get_files_from_zip(document):
    """Find all documents in .zip"""
    import sys
    import zipfile
    import re
    from bs4 import BeautifulSoup

    with zipfile.ZipFile(document, 'r') as zfp:
           n = zfp.namelist()
    return n

def file_contents(name, zipfolder):
    
    with zipfile.ZipFile(zipfolder, 'r') as zfp:
        try:
            with zfp.open(name) as fp:
                soup = fp.read()
        except:
            print('problemer', name)
    return soup

def extract_text(file, zipfolder):
    text = []
    soup = BeautifulSoup(file_contents(file, zipfolder), 'xml')
    for node in soup.find_all('div', {"type":"chapter", "subtype":"source"}):
        for p in node.find_all(['p', 'head']) or p in node_fi:
            text.append(tokenize(p.text))
    return text

def extract_text_as_string(file, zipfolder):
    text = []
    soup = BeautifulSoup(file_contents(file, zipfolder), 'xml')
    for node in soup.find_all('div', {"type":"chapter", "subtype":"source"}):
        for p in node.find_all(['p', 'head']) or p in node_fi:
            text.append(p.text)
    return text

#Se på en og en fil i første omgang, for å ut teksten

def make_corpus(zipfolder, extraction = extract_text):
    texts = dict()
    for f in get_files_from_zip(zipfolder):
        texts[f] = extraction(f, zipfolder)
    return texts



def make_dtm(texts):
    dtm = pd.DataFrame()
    freqs = dict()
    for text in texts.keys():
        print(text)
        c = Counter()
        for p in texts[text]:
            c.update(p)
        freqs[text] = nb.frame(c, text)
    dtm = pd.concat([freqs[text] for text in freqs.keys()], axis=1, sort=False)
    return dtm

def sublist(phrase, alist):
    if phrase == [] or alist == []:
        return None
    found = None
    try:
        ix = alist.index(phrase[0])
        searching = True
        while ix < len(alist) and searching == True:
            if alist[ix: ix + len(phrase)] == phrase:
                if found == None:
                    found = [ix]
                else:
                    found.append(ix)
                try:
                    sublist = alist[ix + len(phrase):]
                    ix += sublist.index(phrase[0])
                except:
                    searching = False
            else:
                ix += 1
    except:
        True
    return found

def konk0(phrase, corpus):    
    return [[p,sublist(phrase, p)] for t in corpus for p in t ]

def coll(phrase, corpus, before = 5, after = 5):
    """Determine collocation within corpus if before and after are both zero the whole paragraph is returned"""
    
    collocation = Counter()
    all_of_paragraph = before == 0 and after == 0
    
    for t in corpus:
        for avsnitt in corpus[t]:
            res = sublist(phrase, avsnitt)
            if res != None:
                for i in res:
                    #print(i, len(phrase), avsnitt[max(i - before - 1, 0): i + len(phrase) + 1 + after])
                    collocation.update(avsnitt[max(i - before - 1, 0): i + len(phrase) + 1 + after])
    return collocation



def konk(phrase, corpus):
    finds = dict()
    # for hver tekst i korpuset
    for t in corpus:
        finds[t] = []
        # hent avsnittene i korpuset
        for i, avsnitt in enumerate(corpus[t]):
            res = sublist(phrase, avsnitt)
            if res != None:
                finds[t].append((i, res))
    return finds



def konk_regex(regex, korpus, before=30, after=30, colour='red'):
    res = []
    for t in korpus:
        found = []
        for i, avsnitt in enumerate(korpus[t]):

            s = re.search(regex, avsnitt)
            if s != None:
                p1 = s.span()[0]
                p2 = s.span()[1]
                found.append(str(i) + ": " + avsnitt.replace(avsnitt[p1:p2], "<span style='color:{c}'>".format(c=colour) + avsnitt[p1:p2] + "</span>")[max(0,p1 - before): p2 + after + 31])
        if found != []:
            res.append("#### " + t)
            res += found
    return res



def korpus_konk(phrase, korpus, before = 10, after = 10):
    actual_konk = konk(phrase, korpus)
    result = ["### Konkordanser for *" + ' '.join(phrase) + "*" ]
    for i in actual_konk:
        if actual_konk[i] != []:
            header = "#### " + str(i)
            result.append(header)
            for hit in actual_konk[i]:
                para = hit[0]
                parahits = hit[1]
                konkstring = []
                for y in parahits:
                    konkstring.append(str(para) + ": " + ' '.join(korpus[i][para][y - before : y+after]))
                result += konkstring
    return result