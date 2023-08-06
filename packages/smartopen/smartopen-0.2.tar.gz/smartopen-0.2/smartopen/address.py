#!/usr/bin/python

import sys
from states import *

def validate_zipcode(zip, zip4=None):
    """ validate a zipcode"""
    
    if not zip:
        # a non-existant zip-code is a valid zipcode
        # ... i think....
        return True 

    if '-' in zip: # in this case, split zip into zip5 + zip4
        zip, zip4 = zip.split('-')

    zdict = { 'zip5': zip, 'zip4': zip4 }
        
    # if the 4-digit extension exists, add it to zip
    if zip4:
        zip += '-' + zip4

    # validate zip code format
    for i in 5, 4:
        zstring = 'zip' + str(i)
        z = zdict.get(zstring, '')
        if z:
            if (not z.isdigit()) or (len(z) != i):
                return False

    return zip

def normalizeaddress(query):
    """ returns normalize address, if it is an address """

    # normalize the address
    query = ','.join([i.strip() for i in query.split('\n')])
    querylist = [i.strip() for i in query.split(',')]
    
    lastentry = querylist[-1]
    
    if lastentry[-1].isdigit():
        # it must be a zip code
        if lastentry[1].isalpha():
            querylist = querylist[:-1] + lastentry.split()
        if not validate_zipcode(querylist[-1]):
            return False
        state = querylist[-2]
    else:
        state = querylist[-1]

    if not getstate(state):
        return False

    return ', '.join(querylist)

def address(query):
    """ 
    format an address 
    -- query should be a string
    """
    
if __name__ == '__main__':
    i = normalizeaddress(' '.join(sys.argv[1:]))
    if i:
        print i
    else:
        print 'Not an address'
        sys.exit(1)
