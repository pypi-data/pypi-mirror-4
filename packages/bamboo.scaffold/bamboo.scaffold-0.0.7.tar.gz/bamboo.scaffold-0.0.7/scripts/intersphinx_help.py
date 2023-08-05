from sphinx.ext.intersphinx import read_inventory_v2
from posixpath import join
import pprint

uri = 'http://docs.scipy.org/doc/numpy/'
inv = '/tmp/objects.inv'

f = open(inv, 'rb')
line = f.readline() # burn a line
invdata = read_inventory_v2(f, uri, join)
pprint.pprint(invdata)
