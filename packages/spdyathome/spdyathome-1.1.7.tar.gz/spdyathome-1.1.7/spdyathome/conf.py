# SPDY@HOME Configuration


# Port for SPDY server to listen on
spdy_port = 38090
# Port for HTTP server to listen on
http_port = 38091
# Port for capture server to listen on
capture_port = 38092

# Host for assets from primary site
mainhost = 'http://spdyathome1.bis12.com'
# Host for assets from secondard site
secondhost = 'http://spdyathome2.bis12.com'

# File containing asset information for each site
sitedump = 'data/sitedump.json'
# File containing the list of sites to access during each test
sitelist = 'data/sitelist_test.txt'

# Directory to write output to
outdir = 'out/'
# File to write output to
outfile = 'report.json'
