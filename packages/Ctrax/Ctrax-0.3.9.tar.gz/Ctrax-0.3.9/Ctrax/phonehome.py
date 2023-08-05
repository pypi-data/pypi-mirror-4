# phonehome.py
# JAB 12/10/11

import httplib
import re
import threading

from version import __version__, DEBUG

VERSION_ADDRESS = "https://downloads.sourceforge.net/project/ctrax/VERSION?r="


#######################################################################
# HomePhoner
#######################################################################
class HomePhoner (threading.Thread):
    """Thread to check downloads website for the latest version of Ctrax."""
    ###################################################################
    # __init__()
    ###################################################################
    def __init__( self, data_callback ):
        threading.Thread.__init__( self )
        self.data_callback = data_callback
        self.start()


    ###################################################################
    # parse_address()
    ###################################################################
    def parse_address( self, address, verbose=False ):
        """Turn a full web address into a host, url, and ssl flag."""
        if verbose: print "initial address", address
        use_ssl = False
        address = re.sub( '^http', '', address )
        if verbose: print "removed http", address
        if re.search( '^s', address ) is not None:
            use_ssl = True
            address = re.sub( '^s', '', address )
            if verbose: print "removed s", address
        address = re.sub( '^\\:\\/\\/', '', address )
        if verbose: print "removed separator", address
        host_match = re.search( '^\w+.*?\w/', address )
        if host_match is not None:
            host = host_match.group( 0 ).rstrip( '/' )
            address = re.sub( host, '', address )
        else:
            host = None
        if verbose: print "host", host
        url = address
        if verbose: print "url", url

        return host, url, use_ssl


    ###################################################################
    # retrieve_from_address()
    ###################################################################
    def retrieve_from_address( self, address ):
        """Get an HTTP response from the specified address."""
        try:
            host, url, use_ssl = self.parse_address( address )
        except:
            # if it fails, run again with verbosity, to aid debugging
            host, url, use_ssl = self.parse_address( address, verbose=True )

        try:
            if use_ssl:
                connection = httplib.HTTPSConnection( host )
            else:
                connection = httplib.HTTPConnection( host )
            connection.request( "GET", url )
            return connection.getresponse()

        except Exception, details:
            print "failed making HTTP connection:", details
            return None
        
        
    ###################################################################
    # run()
    ###################################################################
    def run( self ):
        """Read data from server and parse it."""
        latest_ctrax_version = None
        latest_matlab_version = None

        # get location of VERSION file
        response = self.retrieve_from_address( VERSION_ADDRESS )
        if response is not None:
            if response.status == httplib.FOUND:
                location = response.getheader( 'location' )
                if location is not None:

                    # get VERSION file itself
                    response = self.retrieve_from_address( location )
                    if response is not None:
                        if response.status == httplib.OK:

                            # parse VERSION file
                            data = response.read()
                            for line in data.splitlines():
                                if line.startswith( 'LATEST_CTRAX_VERSION:' ):
                                    s = line.split( ':', 1 )
                                    if len( s ) == 2:
                                        latest_ctrax_version = s[1]
                                elif line.startswith( 'LATEST_MATLAB_VERSION:' ):
                                    s = line.split( ':', 1 )
                                    if len( s ) == 2:
                                        latest_matlab_version = s[1]
                            if latest_ctrax_version is None or latest_matlab_version is None:
                                print "error parsing versions from", data
                                return
                                    
                    if latest_ctrax_version is None or latest_matlab_version is None:
                        print "couldn't retrieve VERSION from", location, response.status, response.reason
                        return

        if latest_ctrax_version is None or latest_matlab_version is None:
            print "couldn't phone home:", response.status, response.reason
            return

        #print latest_ctrax_version, latest_matlab_version
        self.data_callback( latest_ctrax_version, latest_matlab_version )
