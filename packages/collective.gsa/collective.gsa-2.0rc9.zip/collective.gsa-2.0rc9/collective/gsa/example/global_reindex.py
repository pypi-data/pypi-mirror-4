#!/usr/bin/python                                                                                                               

"""
This is an example script for a global reindex if you run into memory problems.

Enter the required information and it will repeatedly index batches of pages on the given system.
If you still encounter problems with memory error, reducing the size of ZODB cache may 
help.

originally written by Steven Hayles ( University of Leicester )
modified by Matous Hora ( Fry-IT ltd.)
"""

import re
import time
import getpass
import urllib, urllib2

pattern = re.compile(".+(Already\\s+reindexed\\s+objects\:\\s+(\\d+)\\s+out\\s+of\\s+(\\d+)).+", re.DOTALL)

def main():
    iteration = 1

    system = raw_input("Enter the external url it would be index under: ")
    username = raw_input("Enter username: ")
    password = getpass.getpass("Enter password: ")
    
    batch_size = raw_input("Enter batch size (default 1000): ")
    batch_size = batch_size is not None and batch_size or 1000
    
    try:
        batch_size = int(batch_size)
    except ValueError, e:
        print "The batch size has to be a number (%s)" % e
        return
        
    iterations = raw_input("Enter number of iterations (default 0 - means everything): ") or 0
    iterations = iterations is not None and iterations or 1000
    
    try:
        iterations = int(iterations)
    except ValueError, e:
        print "The number of interations has to be a number (%s)" % e
        return
    
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, system, username, password)
    
    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
    opener = urllib2.build_opener(handler)

    # at first make sure to start over
    # NOTE: disable this if you want to run it several times
    params = urllib.urlencode({'collective.gsa.startover': 'Start over'})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/html"}
    req = urllib2.Request('%s/@@gsa-maintenance' % system, params, headers)
    response = opener.open(req)
    data = response.read()
    response.close()

    params = urllib.urlencode({'batch_size': batch_size, 'collective.gsa.reindex': 'Reindex next batch'})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/html"}
    
    while iterations == 0 or iterations >= iteration:
        req = urllib2.Request('%s/@@gsa-maintenance' % system, params, headers)
        response = opener.open(req)
        
        status = response.code
        reason = response.msg
        data = response.read()
        result = pattern.match(data)
        if result:
            message = "%d %s %s" % (status, reason, result.groups()[0])
            # break if all is reindexed
            if result.groups()[1] == result.groups()[2]:
                break
        else:
            print "Something wrong has happened, please check the event log to see why the page has not been rendered properly"
            return
            
        print "%d: %s: %s\n" % (iteration, time.strftime("%x %X"), message)

        iteration = iteration + 1

        response.close()

if __name__ == "__main__":
    main()
