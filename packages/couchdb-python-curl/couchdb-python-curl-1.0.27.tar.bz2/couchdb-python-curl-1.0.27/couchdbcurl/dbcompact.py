#!/usr/bin/env python

import sys
from urlparse import urlparse
from optparse import OptionParser
from couchdbcurl.client import Server



def main():
    """
    Entry point.
    """
    
    parser = OptionParser(usage=u"usage: %prog [options] http://example.com:5984/database_name http://example.com:5984/another_database_name ...")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False, help="Be verbose")
    
    (options, args) = parser.parse_args()
    
    if not args:
        parser.print_help()
        sys.exit(3)
    
    for entry in args:
        if options.verbose:
            print 'Parsing entry', entry

        u = urlparse(entry)
        server = '%s://%s' % (u.scheme, u.netloc)
        _server = Server(server)
        path = [s for s in u.path.lstrip('/').split('/') if s]
        
        
        design_doc = None

        if len(path) == 1:
            database = path[0]
            if options.verbose:
                print "  Compacting database - %s at server %s" % (database, _server)

            
            _server[database].compact()
            if options.verbose:
                print "  Compact initiated"
                


        else:
            raise Exception("Error parsing entry path %s" % (entry))


        
        

if __name__ == '__main__':
    main()


