# -*- coding: utf-8 -*-
import urllib, sys

alphabet = map(chr, range(97,123)+range(65,91)) + map(str,range(0,10))

def lookup(k, a=alphabet):
    if type(k) == int:
        return a[k]
    elif type(k) == str:
        return a.index(k)


def encode(i, a=alphabet):
    '''Takes an integer and returns it in the given base with mappings for upper/lower case letters and numbers 0-9.'''
    try:
        i = int(i)
    except Exception:
        raise TypeError("Input must be an integer.")

    def incode(i=i, p=1, a=a):
        # Here to protect p
        if i <= 61:
            return lookup(i)

        else:
            pval = pow(62,p)
            nval = i/pval
            remainder = i % pval
            if nval <= 61:
                return lookup(nval) + incode(i % pval)
            else:
                return incode(i, p+1)

    return incode()



def decode(s, a=alphabet):
    '''Takes a base 62 string in our alphabet and returns it in base10.'''
    try:
        s = str(s)
    except Exception:
        raise TypeError("Input must be a string.")

    return sum([lookup(i) * pow(62,p) for p,i in enumerate(list(reversed(s)))])

def getTitle(url):

    try:
        sock = urllib.urlopen(url)
    except IOError:
        return 'URL not valid: ' + url

    if 'text/' not in sock.headers.type:
        return 'Binary data'
    
    html = sock.read()
    sock.close()

    if not '<title>' in html:
        return 'No title'

    return html[html.find('<title>')+7:html.find('</title>')]
    


